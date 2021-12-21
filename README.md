# sb8200-clickhouse #
An SB8200 exporter for ClickHouse

Configuration is done via environment variables in order to more easily support running it in a container

`⚠️ WARNING: Do not set the scrape delay to <10 seconds or the modem's webserver will crash!`

## Environment Variables ##
```
--- Modem Login Info ---
MODEM_NAME          -   The device name (e.g. "modem", default: "SB8200")
MODEM_URL           -   The modem's URL (e.g. "https://192.168.100.1", default: "https://192.168.100.1")
MODEM_USER          -   The modem's login username (only on newer firmwares)
MODEM_PASS          -   The modem's login password (only on newer firmwares)

--- Scraping Settings ---
SCRAPE_DELAY        -   How long to wait in between scrapes (e.g. "10" for 10 seconds, defaults to "10")

--- ClickHouse Login Info ---
CLICKHOUSE_URL      -   The ClickHouse URL (e.g. "https://192.168.0.69:8123")
CLICKHOUSE_USER     -   The ClickHouse login username
CLICKHOUSE_PASS     -   The ClickHouse login password
CLICKHOUSE_DB       -   The ClickHouse database

--- ClickHouse Table Names ---
DOWNSTREAM_TABLE    -   Downstream stats table name (default: "docsis_downstream")
UPSTREAM_TABLE      -   Upstream stats table name (default: "docsis_upstream")
STATUS_TABLE        -   Modem status table name (default: "docsis_status")
```