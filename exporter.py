import aiochclient
import aiohttp
import asyncio
import datetime
import json
import os
import re

from base64 import b64encode
from bs4 import BeautifulSoup
from traceback import print_exc
from time import perf_counter


# Modem login info
MODEM_NAME = os.environ.get('MODEM_NAME', 'SB8200')
# Please note older firmwares use plain HTTP
MODEM_URL = os.environ.get('MODEM_URL', 'https://192.168.100.1')
# Check if a login username was passed
if (MODEM_USER := os.environ.get('MODEM_USER')):
    MODEM_PASS = os.environ['MODEM_PASS']
    MODEM_AUTH = b64encode(f'{MODEM_USER}:{MODEM_PASS}'.encode()).decode()

UPTIME_REGEX = re.compile(r'(?:([0-9][0-9]?) days )?(?:([0-9][0-9]?)h\:)?(?:([0-9][0-9]?)m\:)?(?:([0-9][0-9]?)s\.00)?')

# Scraping settings
SCRAPE_DELAY = int(os.environ.get('SCRAPE_DELAY', 10))

# ClickHouse login info
CLICKHOUSE_URL = os.environ['CLICKHOUSE_URL']
CLICKHOUSE_USER = os.environ['CLICKHOUSE_USER']
CLICKHOUSE_PASS = os.environ['CLICKHOUSE_PASS']
CLICKHOUSE_DB = os.environ['CLICKHOUSE_DB']

# ClickHouse table names
DOWNSTREAM_TABLE = os.environ.get(
    'CLICKHOUSE_DOWNSTREAM_TABLE',
    'docsis_downstream'
)
UPSTREAM_TABLE = os.environ.get(
    'CLICKHOUSE_UPSTREAM_TABLE',
    'docsis_upstream'
)
STATUS_TABLE = os.environ.get(
    'CLICKHOUSE_STATUS_TABLE',
    'docsis_status'
)


class Exporter:
    async def start(self):
        # Create a ClientSession that doesn't verify SSL certificates
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        )
        self.clickhouse = aiochclient.ChClient(
            self.session,
            url=os.environ['CLICKHOUSE_URL'],
            user=os.environ['CLICKHOUSE_USER'],
            password=os.environ['CLICKHOUSE_PASS'],
            database=os.environ['CLICKHOUSE_DB'],
            json=json
        )
        # Cookies used for auth
        self.cookies = {}

        await self.export()

    async def generate_session(self):
        print('Generating new session...')
        async with self.session.get(
            f'{MODEM_URL}/cmconnectionstatus.html?{MODEM_AUTH}',
            headers={'Authorization': f'Basic {MODEM_AUTH}'},
            timeout=30
        ) as resp:
            self.cookies['credential'] = session = await resp.text()

        print(f'Generated new session: {session}')

    async def export(self):
        if MODEM_USER and not self.cookies:
            await self.generate_session()

        while True:
            try:
                start = perf_counter()
                # main.html shows the loaded config filename
                async with self.session.get(f'{MODEM_URL}/main.html', cookies=self.cookies, timeout=15) as resp:
                    # Use html5lib instead of html.parser
                    # html.parser parses the tables incorrectly
                    html = BeautifulSoup(await resp.text(), 'html5lib')

                # Check if the session expired
                if html.title.text == 'Login':
                    if not MODEM_USER:
                        print('Login required but no username/password passed')
                        exit(1)
                    print('Invalid session detected')
                    # Generate a new session and continue
                    await self.generate_session()
                    continue

                tables = html.find_all('table', class_='simpleTable')
                downstream_html = tables[1].find_all('tr')[2:]
                upstream_html = tables[2].find_all('tr')[2:]
                config_filename = tables[0].find_all('td')[14].text

                # Get the current UTC timestamp
                timestamp = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()

                # Downstream channels
                downstream = []
                for channel in downstream_html:
                    channel = channel.find_all('td')
                    downstream.append((
                        MODEM_NAME,                                 # Passed modem name or SB8200
                        int(channel[0].text),                       # Channel ID
                        float(channel[3].text.replace('Hz', '')),   # Frequency
                        channel[2].text,                            # Modulation
                        float(channel[4].text.replace('dBmV', '')), # Power
                        float(channel[5].text.replace('dB', '')),   # SNR
                        int(channel[6].text),                       # Correcteds
                        int(channel[7].text),                       # Uncorrecteds
                        timestamp
                    ))

                # Upstream channels
                upstream = []
                for channel in upstream_html:
                    channel = channel.find_all('td')
                    upstream.append((
                        MODEM_NAME,                                         # Passed modem name or SB8200
                        int(channel[1].text),                               # Channel ID
                        float(channel[4].text.replace('Hz', '')),           # Frequency
                        channel[3].text.replace('Upstream', '').strip(),    # Modulation
                        float(channel[6].text.replace('dBmV', '')),         # Power
                        float(channel[5].text.replace('Hz', '')),           # Width
                        timestamp
                    ))

                # Insert downstream data into Clickhouse
                await self.clickhouse.execute(
                    f"INSERT INTO {DOWNSTREAM_TABLE} (device, channel_id, frequency, modulation, power, snr, correcteds, uncorrecteds, time) VALUES",
                    *downstream
                )
                # Insert upstream data into Clickhouse
                await self.clickhouse.execute(
                    f"INSERT INTO {UPSTREAM_TABLE} (device, channel_id, frequency, modulation, power, width, time) VALUES",
                    *upstream
                )

                # Device info
                async with self.session.get(f'{MODEM_URL}/cmswinfo.html', cookies=self.cookies, timeout=15) as resp:
                    html = BeautifulSoup(await resp.text(), 'html5lib')
                    tables = html.find_all('table', class_='simpleTable')

                # Uptime
                uptime_groups = UPTIME_REGEX.search(tables[1].find_all('tr')[1].find_all('td')[1].text).groups()
                uptime = 0
                # Days
                if uptime_groups[0]:
                    uptime += int(uptime_groups[0]) * 86400
                # Hours
                if uptime_groups[1]:
                    uptime += int(uptime_groups[1]) * 3600
                # Minutes
                if uptime_groups[2]:
                    uptime += int(uptime_groups[2]) * 60
                # Seconds
                if uptime_groups[3]:
                    uptime += int(uptime_groups[3])

                # How long the scraping took
                latency = perf_counter() - start
                # Insert modem status into Clickhouse
                await self.clickhouse.execute(
                    F"INSERT INTO {STATUS_TABLE} (device, config_filename, uptime, version, model, scrape_latency, time) VALUES",
                    (
                        MODEM_NAME,                                 # Passed modem name or SB8200
                        config_filename,                            # The loaded configuration filename
                        uptime,                                     # System uptime
                        tables[0].find_all('td')[5].text.strip(),   # Software version
                        'SB8200',                                   # Device model
                        latency,                                    # Scrape latency
                        timestamp
                    )
                )
                print(f'Update took {round(latency, 2)}s')
            except Exception:
                print('Failed to update')
                print_exc()
            finally:
                await asyncio.sleep(SCRAPE_DELAY)

loop = asyncio.new_event_loop()
loop.run_until_complete(Exporter().start())