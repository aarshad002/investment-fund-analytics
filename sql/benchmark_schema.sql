-- Explicit benchmark metadata and nonoverlapping project assignments.
-- Apply as project owner; btree_gist is a trusted extension in PostgreSQL.
BEGIN;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE TABLE IF NOT EXISTS core.benchmark (
 benchmark_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 benchmark_code text NOT NULL UNIQUE,
 instrument_id bigint NOT NULL UNIQUE REFERENCES core.instrument(instrument_id),
 benchmark_name text NOT NULL,
 provider_identifier text,
 identifier_notes text NOT NULL,
 benchmark_kind text NOT NULL CHECK(benchmark_kind IN ('official_index','etf_proxy')),
 return_basis text NOT NULL CHECK(return_basis IN ('net_total_return','total_return','accumulating_nav')),
 metadata_url text NOT NULL,
 date_alignment_status text NOT NULL CHECK(date_alignment_status IN ('verified','unverified')),
 limitations text NOT NULL
);
CREATE TABLE IF NOT EXISTS core.benchmark_assignment (
 benchmark_assignment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 fund_instrument_id bigint NOT NULL REFERENCES core.instrument(instrument_id),
 benchmark_id bigint NOT NULL REFERENCES core.benchmark(benchmark_id),
 effective_start_date date NOT NULL,
 effective_end_date date,
 rationale text NOT NULL,
 UNIQUE(fund_instrument_id,effective_start_date),
 CHECK(effective_end_date IS NULL OR effective_end_date>=effective_start_date),
 EXCLUDE USING gist (fund_instrument_id WITH =,
   daterange(effective_start_date,effective_end_date,'[]') WITH &&)
);
CREATE INDEX IF NOT EXISTS benchmark_assignment_benchmark_idx ON core.benchmark_assignment(benchmark_id);
GRANT SELECT,INSERT ON core.benchmark,core.benchmark_assignment TO ifa_app;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA core TO ifa_app;
COMMENT ON TABLE core.benchmark_assignment IS 'Project comparison mapping; dates do not assert historical prospectus assignments outside verified scope.';
COMMIT;
