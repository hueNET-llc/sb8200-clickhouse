# sb8200-clickhouse #
An SB8200 exporter for ClickHouse

`⚠️ WARNING: Setting the scrape delay to <10 seconds may crash the webserver on older firmwares.`

## Environment Variables ##
```
=== Modem ===
MODEM_NAME  -   Modem name (e.g. "modem", default: "SB8200")
MODEM_URL   -   Modem URL (e.g. "https://192.168.100.1", default: "https://192.168.100.1")
MODEM_USER  -   Modem login username (only on newer firmwares)
MODEM_PASS  -   Modem login password (only on newer firmwares)

=== Scraping ===
SCRAPE_DELAY    -   How long to wait in between scrapes (e.g. "10" for 10 seconds, default: "10")

=== ClickHouse ===
CLICKHOUSE_URL                  -   ClickHouse URL (e.g. "https://192.168.0.69:8123")
CLICKHOUSE_USER                 -   ClickHouse login username (e.g. "username")
CLICKHOUSE_PASS                 -   ClickHouse login password (e.g. "password")
CLICKHOUSE_DB                   -   ClickHouse database (e.g. "metrics")
CLICKHOUSE_DOWNSTREAM_TABLE     -   Downstream stats table name (default: "docsis_downstream")
CLICKHOUSE_UPSTREAM_TABLE       -   Upstream stats table name (default: "docsis_upstream")
CLICKHOUSE_STATUS_TABLE         -   Modem status table name (default: "docsis_status")
```