BEGIN;
CREATE OR REPLACE VIEW analytics.controlled_risk_summary AS
WITH eligible AS (
 SELECT * FROM analytics.nav_intervals
 WHERE policy_status='approved_controlled_nav_v1'
 AND proposed_interval_status='eligible_if_policy_approved'
), aggregate AS (
 SELECT instrument_id,isin,min(previous_date) start_date,max(observation_date) end_date,
 count(*) valid_count,stddev_samp(observed_interval_return::double precision)*sqrt(252.0) annualized_volatility,
 sqrt(avg(power(least(observed_interval_return::double precision,0),2))*252) downside_deviation,
 percentile_cont(.05) WITHIN GROUP(ORDER BY observed_interval_return::double precision) cutoff
 FROM eligible GROUP BY instrument_id,isin
)
SELECT a.instrument_id,a.isin,a.start_date,a.end_date,a.valid_count,
 CASE WHEN valid_count>=252 THEN 'eligible' ELSE 'insufficient_history' END status,
 CASE WHEN valid_count>=252 THEN annualized_volatility END annualized_volatility,
 CASE WHEN valid_count>=252 THEN downside_deviation END downside_deviation,
 CASE WHEN valid_count>=252 THEN -cutoff END var_95,
 CASE WHEN valid_count>=252 THEN (SELECT -avg(e.observed_interval_return::double precision) FROM eligible e
 WHERE e.instrument_id=a.instrument_id AND e.observed_interval_return::double precision<=a.cutoff) END expected_shortfall_95,
 CASE WHEN valid_count>=252 THEN (SELECT count(*) FROM eligible e WHERE e.instrument_id=a.instrument_id
 AND e.observed_interval_return::double precision<=a.cutoff) END tail_count
FROM aggregate a;
CREATE OR REPLACE VIEW analytics.controlled_rolling_volatility AS
WITH inputs AS (
 SELECT *,CASE WHEN policy_status='approved_controlled_nav_v1' AND proposed_interval_status='eligible_if_policy_approved'
 THEN observed_interval_return::double precision END risk_return FROM analytics.nav_intervals
), windows AS (
 SELECT instrument_id,isin,observation_date,interval_days,
 count(risk_return) OVER w63 count_63,stddev_samp(risk_return) OVER w63 sd63,
 count(risk_return) OVER w252 count_252,stddev_samp(risk_return) OVER w252 sd252
 FROM inputs WINDOW w63 AS (PARTITION BY instrument_id ORDER BY observation_date ROWS BETWEEN 62 PRECEDING AND CURRENT ROW),
 w252 AS (PARTITION BY instrument_id ORDER BY observation_date ROWS BETWEEN 251 PRECEDING AND CURRENT ROW)
)
SELECT instrument_id,isin,observation_date,interval_days,count_63,count_252,
 CASE WHEN count_63=63 THEN sd63*sqrt(252.0) END volatility_63,
 CASE WHEN count_252=252 THEN sd252*sqrt(252.0) END volatility_252 FROM windows;
GRANT SELECT ON analytics.controlled_risk_summary,analytics.controlled_rolling_volatility TO ifa_app;
COMMIT;
