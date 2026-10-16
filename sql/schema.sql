-- Phase 1: PostgreSQL 16+; no seed data or analytical logic.
-- Run as dedicated schema owner in the intended database.
-- Repeatable for an unchanged schema; IF NOT EXISTS is not a migration tool.
BEGIN;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS core.fund_share_class (
    fund_share_class_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    isin varchar(12) NOT NULL UNIQUE CHECK (isin ~ '^[A-Z]{2}[A-Z0-9]{9}[0-9]$'),
    fund_name text NOT NULL CHECK (btrim(fund_name) <> ''),
    share_class_name text NOT NULL CHECK (btrim(share_class_name) <> ''),
    issuer_name text NOT NULL CHECK (btrim(issuer_name) <> ''),
    legal_umbrella text,
    domicile_country_code varchar(2) NOT NULL CHECK (domicile_country_code ~ '^[A-Z]{2}$'),
    asset_class text NOT NULL CHECK (asset_class IN ('equity', 'bond', 'cash_like', 'mixed', 'other')),
    category text NOT NULL CHECK (btrim(category) <> ''),
    income_policy text NOT NULL CHECK (income_policy IN ('accumulating', 'distributing')),
    share_class_currency varchar(3) NOT NULL CHECK (share_class_currency ~ '^[A-Z]{3}$'),
    hedging_policy text NOT NULL CHECK (hedging_policy IN ('unhedged', 'hedged', 'unknown')),
    hedge_currency varchar(3) CHECK (hedge_currency ~ '^[A-Z]{3}$'),
    inception_date date,
    ucits_status boolean NOT NULL,
    benchmark_name text,
    metadata_source_url text NOT NULL CHECK (metadata_source_url ~ '^https?://'),
    metadata_as_of_date date NOT NULL,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ((hedging_policy = 'hedged' AND hedge_currency IS NOT NULL)
        OR (hedging_policy IN ('unhedged', 'unknown') AND hedge_currency IS NULL))
);

CREATE TABLE IF NOT EXISTS core.instrument (
    instrument_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instrument_code text NOT NULL UNIQUE CHECK (btrim(instrument_code) <> ''),
    fund_share_class_id bigint REFERENCES core.fund_share_class (fund_share_class_id),
    instrument_name text NOT NULL CHECK (btrim(instrument_name) <> ''),
    instrument_type text NOT NULL CHECK (instrument_type IN ('fund_nav', 'etf_listing', 'index')),
    value_basis text NOT NULL CHECK (value_basis IN ('nav', 'market_close', 'adjusted_close', 'total_return_index')),
    currency varchar(3) NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    adjustment_status text NOT NULL CHECK (adjustment_status IN ('native', 'provider_adjusted', 'total_return', 'unknown')),
    adjustment_notes text,
    ticker text,
    exchange_mic varchar(4) CHECK (exchange_mic ~ '^[A-Z0-9]{4}$'),
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        (instrument_type = 'fund_nav' AND fund_share_class_id IS NOT NULL
            AND value_basis = 'nav' AND ticker IS NULL AND exchange_mic IS NULL)
        OR (instrument_type = 'etf_listing' AND fund_share_class_id IS NOT NULL
            AND value_basis IN ('market_close', 'adjusted_close')
            AND ticker IS NOT NULL AND btrim(ticker) <> '' AND exchange_mic IS NOT NULL)
        OR (instrument_type = 'index' AND fund_share_class_id IS NULL
            AND value_basis IN ('market_close', 'total_return_index')
            AND ticker IS NULL AND exchange_mic IS NULL)
    )
);
CREATE INDEX IF NOT EXISTS instrument_share_class_idx ON core.instrument (fund_share_class_id);
CREATE UNIQUE INDEX IF NOT EXISTS instrument_nav_identity_uq
    ON core.instrument (fund_share_class_id, currency, value_basis) WHERE instrument_type = 'fund_nav';
CREATE UNIQUE INDEX IF NOT EXISTS instrument_listing_identity_uq
    ON core.instrument (fund_share_class_id, exchange_mic, ticker, currency, value_basis)
    WHERE instrument_type = 'etf_listing';

CREATE TABLE IF NOT EXISTS core.source (
    source_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_code text NOT NULL UNIQUE CHECK (btrim(source_code) <> ''),
    provider_name text NOT NULL CHECK (btrim(provider_name) <> ''),
    source_name text NOT NULL CHECK (btrim(source_name) <> ''),
    source_url text NOT NULL CHECK (source_url ~ '^https?://'),
    access_method text NOT NULL CHECK (access_method IN ('http_xlsx', 'http_csv', 'http_json', 'manual_download')),
    authentication_required boolean,
    terms_url text CHECK (terms_url ~ '^https?://'),
    terms_reviewed_on date,
    local_use_status text NOT NULL DEFAULT 'unresolved' CHECK (local_use_status IN ('permitted', 'restricted', 'unresolved')),
    redistribution_status text NOT NULL DEFAULT 'unresolved' CHECK (redistribution_status IN ('permitted', 'restricted', 'unresolved')),
    permission_notes text,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.ingestion_run (
    ingestion_run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id bigint NOT NULL REFERENCES core.source (source_id),
    instrument_id bigint NOT NULL REFERENCES core.instrument (instrument_id),
    started_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamptz,
    retrieved_at timestamptz,
    status text NOT NULL DEFAULT 'started' CHECK (status IN ('started', 'succeeded', 'failed')),
    request_url text CHECK (request_url ~ '^https?://'),
    request_parameters jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(request_parameters) = 'object'),
    requested_start_date date,
    requested_end_date date,
    observed_start_date date,
    observed_end_date date,
    raw_file_path text,
    file_sha256 varchar(64) CHECK (file_sha256 ~ '^[a-f0-9]{64}$'),
    file_bytes bigint CHECK (file_bytes >= 0),
    rows_read integer CHECK (rows_read >= 0),
    rows_accepted integer CHECK (rows_accepted >= 0),
    rows_rejected integer CHECK (rows_rejected >= 0),
    rows_inserted integer CHECK (rows_inserted >= 0),
    pipeline_version text,
    error_message text,
    UNIQUE (ingestion_run_id, instrument_id),
    CHECK ((requested_start_date IS NULL AND requested_end_date IS NULL)
        OR (requested_start_date IS NOT NULL AND requested_end_date IS NOT NULL AND requested_start_date <= requested_end_date)),
    CHECK ((observed_start_date IS NULL AND observed_end_date IS NULL)
        OR (observed_start_date IS NOT NULL AND observed_end_date IS NOT NULL AND observed_start_date <= observed_end_date)),
    CHECK (completed_at IS NULL OR completed_at >= started_at),
    CHECK ((status = 'started' AND completed_at IS NULL)
        OR (status IN ('succeeded', 'failed') AND completed_at IS NOT NULL)),
    CHECK (rows_read IS NULL OR rows_accepted IS NULL OR rows_rejected IS NULL OR rows_read = rows_accepted + rows_rejected),
    CHECK (rows_inserted IS NULL OR rows_accepted IS NULL OR rows_inserted <= rows_accepted),
    CHECK (status <> 'succeeded' OR (
        retrieved_at IS NOT NULL AND raw_file_path IS NOT NULL AND file_sha256 IS NOT NULL
        AND file_bytes IS NOT NULL AND rows_read IS NOT NULL AND rows_accepted IS NOT NULL
        AND rows_rejected IS NOT NULL AND rows_inserted IS NOT NULL AND pipeline_version IS NOT NULL
    ))
);
CREATE INDEX IF NOT EXISTS ingestion_run_source_idx ON core.ingestion_run (source_id);
CREATE INDEX IF NOT EXISTS ingestion_run_instrument_time_idx ON core.ingestion_run (instrument_id, started_at DESC);
CREATE INDEX IF NOT EXISTS ingestion_run_checksum_idx ON core.ingestion_run (file_sha256);

CREATE TABLE IF NOT EXISTS core.observation (
    instrument_id bigint NOT NULL REFERENCES core.instrument (instrument_id),
    observation_date date NOT NULL,
    value numeric(20,10) NOT NULL CHECK (value > 0 AND value NOT IN ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)),
    ingestion_run_id bigint NOT NULL,
    raw_row_number integer CHECK (raw_row_number > 0),
    quality_status text NOT NULL DEFAULT 'valid' CHECK (quality_status IN ('valid', 'flagged')),
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (instrument_id, observation_date),
    FOREIGN KEY (ingestion_run_id, instrument_id) REFERENCES core.ingestion_run (ingestion_run_id, instrument_id)
);
CREATE INDEX IF NOT EXISTS observation_date_idx ON core.observation (observation_date);
CREATE INDEX IF NOT EXISTS observation_run_idx ON core.observation (ingestion_run_id);

CREATE TABLE IF NOT EXISTS core.quality_issue (
    quality_issue_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingestion_run_id bigint NOT NULL,
    instrument_id bigint NOT NULL REFERENCES core.instrument (instrument_id),
    observation_date date,
    raw_row_number integer CHECK (raw_row_number > 0),
    check_code text NOT NULL CHECK (btrim(check_code) <> ''),
    severity text NOT NULL CHECK (severity IN ('info', 'warning', 'error')),
    details text NOT NULL CHECK (btrim(details) <> ''),
    issue_status text NOT NULL DEFAULT 'open' CHECK (issue_status IN ('open', 'resolved', 'accepted')),
    resolution_notes text,
    resolved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ingestion_run_id, instrument_id) REFERENCES core.ingestion_run (ingestion_run_id, instrument_id),
    CHECK ((issue_status = 'open' AND resolved_at IS NULL)
        OR (issue_status IN ('resolved', 'accepted') AND resolved_at IS NOT NULL
            AND resolution_notes IS NOT NULL AND btrim(resolution_notes) <> '')),
    CHECK (resolved_at IS NULL OR resolved_at >= created_at)
);
CREATE INDEX IF NOT EXISTS quality_issue_run_idx ON core.quality_issue (ingestion_run_id);
CREATE INDEX IF NOT EXISTS quality_issue_instrument_date_idx ON core.quality_issue (instrument_id, observation_date);
CREATE INDEX IF NOT EXISTS quality_issue_open_idx ON core.quality_issue (severity, instrument_id) WHERE issue_status = 'open';

COMMENT ON SCHEMA staging IS 'Reserved for future parsed/rejected source records; empty in Phase 1.';
COMMENT ON SCHEMA analytics IS 'Reserved for future return/risk tables and views; empty in Phase 1.';
COMMENT ON TABLE core.observation IS 'One current positive value per instrument/date; basis/currency belong to instrument.';
COMMENT ON TABLE core.ingestion_run IS 'One attempt per source, instrument and file; repeated attempts retained.';
COMMENT ON TABLE core.quality_issue IS 'May refer to rejected source rows; intentionally no observation foreign key.';
COMMIT;
