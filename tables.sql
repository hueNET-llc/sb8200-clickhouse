-- PLEASE NOTE
-- These buffer tables are what I personally use to do batch inserts
-- You may have to modify them to work in your setup

CREATE TABLE docsis_downstream (
        device LowCardinality(String),
        channel_id smallint,
        frequency float,
        modulation LowCardinality(String),
        power float,
        snr float,
        correcteds bigint,
        uncorrecteds bigint,
        time DateTime DEFAULT now()
    ) ENGINE = MergeTree() PARTITION BY toDate(time) ORDER BY (device, channel_id, time) PRIMARY KEY (device, channel_id, time);

CREATE TABLE docsis_downstream_buffer (
        device LowCardinality(String),
        channel_id smallint,
        frequency float,
        modulation LowCardinality(String),
        power float,
        snr float,
        correcteds bigint,
        uncorrecteds bigint,
        time DateTime DEFAULT now()
    ) ENGINE = Buffer(homelab, docsis_downstream, 1, 10, 10, 10, 100, 10000, 10000);

CREATE TABLE docsis_upstream (
        device LowCardinality(String),
        channel_id smallint,
        frequency float,
        modulation LowCardinality(String),
        power float,
        width float,
        time DateTime DEFAULT now()
    ) ENGINE = MergeTree() PARTITION BY toDate(time) ORDER BY (device, channel_id, time) PRIMARY KEY (device, channel_id, time);

CREATE TABLE docsis_upstream_buffer (
        device LowCardinality(String),
        channel_id smallint,
        frequency float,
        modulation LowCardinality(String),
        power float,
        width float,
        time DateTime DEFAULT now()
    ) ENGINE = Buffer(homelab, docsis_upstream, 1, 10, 10, 10, 100, 10000, 10000);

CREATE TABLE docsis_status (
        device LowCardinality(String),
        config_filename LowCardinality(Nullable(String)),
        uptime bigint,
        version LowCardinality(String),
        model LowCardinality(String),
        scrape_latency float,
        time DateTime DEFAULT now()
    ) ENGINE = MergeTree() PARTITION BY toDate(time) ORDER BY (device, time) PRIMARY KEY (device, time);

CREATE TABLE docsis_status_buffer (
        device LowCardinality(String),
        config_filename LowCardinality(Nullable(String)),
        uptime bigint,
        version LowCardinality(String),
        model LowCardinality(String),
        scrape_latency float,
        time DateTime DEFAULT now()
    ) ENGINE = Buffer(homelab, docsis_status, 1, 10, 10, 10, 100, 10000, 10000);
