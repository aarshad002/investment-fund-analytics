-- Approved controlled observed-NAV policy; no cash or benchmark metrics.
BEGIN;
CREATE OR REPLACE VIEW analytics.nav_intervals AS
SELECT n.*,n.observation_date-n.previous_date AS interval_days,
       n.nav/n.previous_nav-1 AS observed_interval_return,
       CASE WHEN n.previous_date IS NULL THEN 'no_prior_observation'
            WHEN n.previous_date<DATE '2023-12-01' OR n.observation_date>DATE '2026-09-30' THEN 'outside_proposed_risk_window'
            WHEN n.quality_status<>'valid' OR p.quality_status<>'valid' THEN 'flagged_boundary'
            WHEN EXISTS (
              SELECT 1 FROM generate_series(n.previous_date+1,n.observation_date-1,interval '1 day') g(day)
              WHERE EXTRACT(isodow FROM g.day)<6 AND NOT EXISTS (
                SELECT 1 FROM analytics.calendar_gaps q WHERE q.instrument_id=n.instrument_id
                AND q.observation_date=g.day::date AND q.classification='expected/non-valuation day'))
              THEN 'unexplained_or_unapproved_weekday_gap'
            ELSE 'eligible_if_policy_approved' END AS proposed_interval_status,
       'approved_controlled_nav_v1'::text AS policy_status
FROM analytics.daily_nav n
LEFT JOIN core.observation p ON p.instrument_id=n.instrument_id AND p.observation_date=n.previous_date;
GRANT SELECT ON analytics.nav_intervals TO ifa_app;
COMMIT;
