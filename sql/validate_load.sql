-- Read-only post-load diagnostics. Not executed until PostgreSQL and loader exist.
-- Run before and after a second load; counts AND fingerprints must match.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL TIME ZONE 'UTC';

SELECT version() AS server_version;

WITH approved(isin) AS (
    VALUES ('LU0380865021'), ('LU0290355717')
)
SELECT a.isin, i.instrument_code, i.currency, i.value_basis, i.adjustment_status,
       COUNT(o.observation_date) AS observation_count,
       MIN(o.observation_date) AS earliest, MAX(o.observation_date) AS latest,
       COUNT(*) FILTER (WHERE o.value <= 0 OR o.value::text IN ('NaN','Infinity','-Infinity')) AS invalid_values,
       -- Includes values, quality and original run/row lineage; not a security checksum.
       MD5(STRING_AGG(CONCAT_WS('|', o.observation_date, o.value,
                               o.quality_status, o.ingestion_run_id, o.raw_row_number),
                      ';' ORDER BY o.observation_date)) AS observation_fingerprint
FROM approved a
LEFT JOIN core.fund_share_class f ON f.isin = a.isin
LEFT JOIN core.instrument i ON i.fund_share_class_id = f.fund_share_class_id
    AND i.instrument_type = 'fund_nav' AND i.currency = 'EUR'
LEFT JOIN core.observation o ON o.instrument_id = i.instrument_id
GROUP BY a.isin, i.instrument_code, i.currency, i.value_basis, i.adjustment_status
ORDER BY a.isin;

SELECT instrument_id, observation_date, COUNT(*) AS duplicates
FROM core.observation GROUP BY instrument_id, observation_date HAVING COUNT(*) > 1;

SELECT 'observation_instrument' AS relationship, COUNT(*) AS orphan_count
FROM core.observation o LEFT JOIN core.instrument i USING (instrument_id)
WHERE i.instrument_id IS NULL
UNION ALL
SELECT 'observation_run_instrument', COUNT(*)
FROM core.observation o LEFT JOIN core.ingestion_run r
ON (o.ingestion_run_id = r.ingestion_run_id AND o.instrument_id = r.instrument_id)
WHERE r.ingestion_run_id IS NULL
UNION ALL
SELECT 'instrument_fund', COUNT(*)
FROM core.instrument i LEFT JOIN core.fund_share_class f USING (fund_share_class_id)
WHERE i.fund_share_class_id IS NOT NULL AND f.fund_share_class_id IS NULL
UNION ALL
SELECT 'run_source', COUNT(*)
FROM core.ingestion_run r LEFT JOIN core.source s USING (source_id)
WHERE s.source_id IS NULL
UNION ALL
SELECT 'run_instrument', COUNT(*)
FROM core.ingestion_run r LEFT JOIN core.instrument i USING (instrument_id)
WHERE i.instrument_id IS NULL
UNION ALL
SELECT 'quality_run_instrument', COUNT(*)
FROM core.quality_issue q LEFT JOIN core.ingestion_run r
ON (q.ingestion_run_id = r.ingestion_run_id AND q.instrument_id = r.instrument_id)
WHERE r.ingestion_run_id IS NULL;

SELECT s.source_code, i.instrument_code, r.ingestion_run_id, r.status,
       r.rows_read, r.rows_accepted, r.rows_rejected, r.rows_inserted,
       r.file_sha256, r.retrieved_at, r.observed_start_date, r.observed_end_date
FROM core.ingestion_run r
JOIN core.source s USING (source_id)
JOIN core.instrument i USING (instrument_id)
ORDER BY r.ingestion_run_id;

SELECT check_code, issue_status, severity, COUNT(*) AS issues
FROM core.quality_issue GROUP BY check_code, issue_status, severity
ORDER BY check_code, issue_status, severity;
COMMIT;
