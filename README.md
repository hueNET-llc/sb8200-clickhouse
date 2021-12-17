# sb8200-clickhouse #
An SB8200 exporter for ClickHouse

Configuration is done via environment variables in order to more easily support running it in a container

`⚠️ WARNING: Do not set the scrape delay too low or the modem's webserver will eventually CRASH!`

## Environment Variables ##
```
MODEM_NAME      -   The device name (i.e. "modem", defaults to "SB8200")
MODEM_URL       -   The modem's URL (i.e. "https://192.168.100.1", defaults to "https://192.168.100.1")
MODEM_USER      -   The modem's login username (only on newer firmwares)
MODEM_PASS      -   The modem's login password (only on newer firmwares)

SCRAPE_DELAY    -   How long to wait in between scrapes (i.e. "10" for 10 seconds, defaults to "10")

CLICKHOUSE_URL  -   The ClickHouse URL (i.e. "https://192.168.0.69:8123")
CLICKHOUSE_USER -   The ClickHouse login username
CLICKHOUSE_PASS -   The ClickHouse login password
CLICKHOUSE_DB   -   The ClickHouse database
```