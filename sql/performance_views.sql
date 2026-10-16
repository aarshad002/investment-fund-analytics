-- Phase 4: observed native NAV performance only; no daily risk estimation.
BEGIN;
CREATE OR REPLACE VIEW analytics.daily_nav AS
SELECT f.isin,i.instrument_id,o.observation_date,o.value AS nav,o.quality_status,
       i.currency,i.value_basis,o.ingestion_run_id,
       LAG(o.observation_date) OVER w AS previous_date,
       LAG(o.value) OVER w AS previous_nav
FROM core.observation o JOIN core.instrument i USING(instrument_id)
JOIN core.fund_share_class f USING(fund_share_class_id)
WHERE f.isin IN ('LU0380865021','LU0290355717') AND i.instrument_type='fund_nav'
  AND i.currency='EUR' AND i.value_basis='nav'
WINDOW w AS (PARTITION BY i.instrument_id ORDER BY o.observation_date);

CREATE OR REPLACE VIEW analytics.calendar_gaps AS
SELECT DISTINCT instrument_id,observation_date,
       details::jsonb->>'classification' AS classification
FROM core.quality_issue WHERE check_code='calendar_gap';

CREATE OR REPLACE VIEW analytics.period_returns AS
WITH grouped AS (
 SELECT n.isin,n.instrument_id,k.period_type,
        date_trunc(k.period_type,n.observation_date)::date AS period_start,
        (array_agg(n.previous_date ORDER BY n.observation_date))[1] AS boundary_date,
        (array_agg(n.previous_nav ORDER BY n.observation_date))[1] AS boundary_nav,
        MIN(n.observation_date) AS first_observation,
        MAX(n.observation_date) AS end_date,
        (array_agg(n.nav ORDER BY n.observation_date DESC))[1] AS end_nav,
        (array_agg(n.nav ORDER BY n.observation_date))[1] AS first_nav,
        COUNT(*) AS observations,
        SUM(LN(n.nav/n.previous_nav)) FILTER(WHERE n.previous_nav IS NOT NULL) AS log_growth,
        BOOL_OR(n.quality_status='flagged') AS flagged
 FROM analytics.daily_nav n CROSS JOIN (VALUES ('month'),('year')) k(period_type)
 GROUP BY n.isin,n.instrument_id,k.period_type,date_trunc(k.period_type,n.observation_date)
), bounded AS (
 SELECT g.*, (period_start + CASE WHEN period_type='month' THEN interval '1 month' ELSE interval '1 year' END - interval '1 day')::date AS period_end,
        (SELECT MAX(observation_date) FROM analytics.daily_nav n WHERE n.instrument_id=g.instrument_id) AS as_of
 FROM grouped g
), tagged AS (
 SELECT b.*, CASE
   WHEN boundary_date IS NULL OR date_trunc(period_type,boundary_date)::date <
       (period_start - CASE WHEN period_type='month' THEN interval '1 month' ELSE interval '1 year' END)::date
       OR as_of<period_end THEN 'partial_period'
   WHEN period_start-boundary_date>7 OR period_end-end_date>7 THEN 'stale_boundary'
   WHEN flagged THEN 'flagged_path'
   WHEN EXISTS(SELECT 1 FROM analytics.calendar_gaps q WHERE q.instrument_id=b.instrument_id
       AND q.observation_date>boundary_date AND q.observation_date<=period_end AND q.classification='unresolved') THEN 'unresolved_gap'
   WHEN EXISTS(SELECT 1 FROM analytics.calendar_gaps q WHERE q.instrument_id=b.instrument_id
       AND q.observation_date>boundary_date AND q.observation_date<=period_end AND q.classification='likely legitimate') THEN 'calendar_review'
   ELSE 'observed_boundaries' END AS status
 FROM bounded b
)
SELECT *, COALESCE(end_nav/boundary_nav-1,end_nav/first_nav-1) AS observed_return,
 CASE WHEN status IN ('partial_period','stale_boundary','flagged_path') THEN NULL
      ELSE EXP(log_growth)-1 END AS period_return
FROM tagged;
CREATE OR REPLACE VIEW analytics.monthly_returns AS SELECT * FROM analytics.period_returns WHERE period_type='month';
CREATE OR REPLACE VIEW analytics.calendar_year_returns AS SELECT * FROM analytics.period_returns WHERE period_type='year';

CREATE OR REPLACE VIEW analytics.cumulative_return AS
SELECT *, nav/FIRST_VALUE(nav) OVER w-1 AS cumulative_return,
       FIRST_VALUE(observation_date) OVER w AS start_date
FROM analytics.daily_nav
WINDOW w AS (PARTITION BY instrument_id ORDER BY observation_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW);

CREATE OR REPLACE VIEW analytics.common_window AS
WITH shared AS (SELECT observation_date FROM analytics.daily_nav GROUP BY observation_date
 HAVING COUNT(DISTINCT instrument_id)=(SELECT COUNT(DISTINCT instrument_id) FROM analytics.daily_nav))
SELECT MIN(observation_date) AS start_date,MAX(observation_date) AS end_date FROM shared;

CREATE OR REPLACE VIEW analytics.drawdown_series AS
SELECT n.*,w.start_date AS window_start,w.end_date AS window_end,
       MAX(nav) OVER (PARTITION BY instrument_id ORDER BY observation_date ROWS UNBOUNDED PRECEDING) AS running_peak,
       nav/MAX(nav) OVER (PARTITION BY instrument_id ORDER BY observation_date ROWS UNBOUNDED PRECEDING)-1 AS drawdown
FROM analytics.daily_nav n CROSS JOIN analytics.common_window w
WHERE observation_date BETWEEN w.start_date AND w.end_date;

CREATE OR REPLACE VIEW analytics.maximum_drawdown AS
WITH worst AS MATERIALIZED (SELECT DISTINCT ON(instrument_id) * FROM analytics.drawdown_series
 ORDER BY instrument_id,drawdown,observation_date), peaks AS MATERIALIZED (
 SELECT w.*,CASE WHEN drawdown<0 THEN (SELECT MAX(p.observation_date) FROM analytics.drawdown_series p
 WHERE p.instrument_id=w.instrument_id AND p.observation_date<w.observation_date AND p.nav=w.running_peak) END AS peak_date
 FROM worst w
), recovery AS MATERIALIZED (
 SELECT p.*,CASE WHEN drawdown<0 THEN (SELECT MIN(r.observation_date) FROM analytics.drawdown_series r
 WHERE r.instrument_id=p.instrument_id AND r.observation_date>p.observation_date AND r.nav>=p.running_peak) END AS recovery_date
 FROM peaks p
)
SELECT isin,instrument_id,drawdown AS max_drawdown,peak_date,
       CASE WHEN drawdown<0 THEN observation_date END AS trough_date,recovery_date,
       CASE WHEN drawdown=0 THEN 'not_applicable' WHEN recovery_date IS NULL THEN 'ongoing' ELSE 'recovered' END AS recovery_status,
       recovery_date-peak_date AS recovery_duration_days,
       CASE WHEN drawdown<0 AND recovery_date IS NULL THEN window_end-peak_date END AS ongoing_duration_days
FROM recovery;

CREATE OR REPLACE VIEW analytics.common_window_comparison AS
WITH d AS MATERIALIZED (SELECT * FROM analytics.maximum_drawdown)
SELECT n.isin,n.instrument_id,w.start_date,w.end_date,COUNT(*) AS observations,
 (array_agg(nav ORDER BY observation_date DESC))[1]/(array_agg(nav ORDER BY observation_date))[1]-1 AS cumulative_return,
 CASE WHEN w.end_date>= (w.start_date+interval '1 year')::date THEN
 POWER((array_agg(nav ORDER BY observation_date DESC))[1]/(array_agg(nav ORDER BY observation_date))[1],
       365.25/(w.end_date-w.start_date))-1 END AS cagr,
 d.max_drawdown,d.peak_date,d.trough_date,d.recovery_date,d.recovery_status,d.recovery_duration_days,d.ongoing_duration_days,
 'native_nav_change; observed_path_drawdown; calendar_caveat'::text AS basis_status
FROM analytics.daily_nav n CROSS JOIN analytics.common_window w JOIN d USING(instrument_id,isin)
WHERE n.observation_date BETWEEN w.start_date AND w.end_date
GROUP BY n.isin,n.instrument_id,w.start_date,w.end_date,d.max_drawdown,d.peak_date,d.trough_date,d.recovery_date,d.recovery_status,d.recovery_duration_days,d.ongoing_duration_days;
GRANT USAGE ON SCHEMA analytics TO ifa_app;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO ifa_app;
COMMIT;
