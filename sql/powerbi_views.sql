-- Presentation only: reuse validated metrics without changing calculations.
BEGIN;
CREATE OR REPLACE VIEW analytics.pbi_fund_overview AS
SELECT i.instrument_id,i.instrument_code,f.isin,f.fund_name,f.issuer_name,
 f.asset_class,f.category,f.domicile_country_code,f.share_class_currency,
 i.currency,f.income_policy,f.hedging_policy,f.benchmark_name,
 'Benchmark name is metadata only; benchmark-relative metrics unavailable'::text benchmark_status,
 'Native accumulating EUR NAV; observed-path performance; controlled zero-target NAV risk'::text methodology_notes
FROM core.instrument i JOIN core.fund_share_class f USING(fund_share_class_id)
WHERE i.instrument_id IN (SELECT DISTINCT instrument_id FROM analytics.daily_nav);

CREATE OR REPLACE VIEW analytics.pbi_date AS
SELECT day::date date_key,extract(year FROM day)::integer calendar_year,
 extract(month FROM day)::integer month_number,to_char(day,'Mon') month_name,
 date_trunc('month',day)::date month_start,to_char(day,'YYYY-MM') year_month,
 extract(quarter FROM day)::integer quarter,extract(isodow FROM day)::integer weekday_number
FROM generate_series(
 date_trunc('year',(SELECT min(observation_date) FROM analytics.daily_nav)),
 date_trunc('year',(SELECT max(observation_date) FROM analytics.daily_nav))+interval '1 year'-interval '1 day',
 interval '1 day') day;

CREATE OR REPLACE VIEW analytics.pbi_daily_performance AS
SELECT instrument_id,observation_date date_key,nav,currency,value_basis,
 start_date base_date,cumulative_return,100*(1+cumulative_return) rebased_nav,
 previous_date,observation_date-previous_date interval_days,quality_status,ingestion_run_id
FROM analytics.cumulative_return;

CREATE OR REPLACE VIEW analytics.pbi_monthly_returns AS
SELECT instrument_id,period_start date_key,period_end,boundary_date,end_date,
 observations,period_return,observed_return partial_or_observed_return,status
FROM analytics.monthly_returns;

CREATE OR REPLACE VIEW analytics.pbi_calendar_year_returns AS
SELECT instrument_id,period_start date_key,period_end,boundary_date,end_date,
 observations,period_return,observed_return partial_or_observed_return,status
FROM analytics.calendar_year_returns;

CREATE OR REPLACE VIEW analytics.pbi_drawdowns AS
SELECT instrument_id,observation_date date_key,nav,running_peak,drawdown,
 window_start,window_end,ingestion_run_id FROM analytics.drawdown_series;

CREATE OR REPLACE VIEW analytics.pbi_performance_snapshot AS
SELECT instrument_id,'full_history_common_window'::text window_key,end_date date_key,
 start_date,end_date,observations,cumulative_return,cagr,max_drawdown,peak_date,trough_date,
 recovery_date,recovery_status,recovery_duration_days,ongoing_duration_days,basis_status
FROM analytics.common_window_comparison;

CREATE OR REPLACE VIEW analytics.pbi_risk_snapshot AS
SELECT s.instrument_id,'controlled_nav_20231201_20260930'::text window_key,s.end_date date_key,
 s.start_date,s.end_date,s.valid_count,s.status,s.annualized_volatility,s.downside_deviation,
 s.var_95,s.expected_shortfall_95,s.tail_count,r.volatility_63 latest_volatility_63,
 r.volatility_252 latest_volatility_252,r.count_63 latest_count_63,r.count_252 latest_count_252,
 252::integer annualization_intervals,0::numeric downside_target,
 'Eligible NAV valuation intervals; variable elapsed days; zero downside target'::text methodology_notes
FROM analytics.controlled_risk_summary s LEFT JOIN analytics.controlled_rolling_volatility r
 ON r.instrument_id=s.instrument_id AND r.observation_date=s.end_date;

CREATE OR REPLACE VIEW analytics.pbi_rolling_63 AS
SELECT instrument_id,observation_date date_key,interval_days,count_63 valid_count,
 volatility_63 annualized_volatility FROM analytics.controlled_rolling_volatility;
CREATE OR REPLACE VIEW analytics.pbi_rolling_252 AS
SELECT instrument_id,observation_date date_key,interval_days,count_252 valid_count,
 volatility_252 annualized_volatility FROM analytics.controlled_rolling_volatility;

CREATE OR REPLACE VIEW analytics.pbi_quality_summary AS
WITH coverage AS (
 SELECT instrument_id,min(observation_date) first_nav_date,max(observation_date) last_nav_date,
 count(*) observation_count,count(*) FILTER(WHERE quality_status='flagged') flagged_nav_count
 FROM analytics.daily_nav GROUP BY instrument_id
), gaps AS (
 SELECT instrument_id,count(*) absent_weekdays,
 count(*) FILTER(WHERE classification='expected/non-valuation day') expected_closures,
 count(*) FILTER(WHERE classification='likely legitimate') likely_legitimate_gaps,
 count(*) FILTER(WHERE classification='unresolved') unresolved_gaps
 FROM analytics.calendar_gaps GROUP BY instrument_id
), intervals AS (
 SELECT instrument_id,count(*) FILTER(WHERE proposed_interval_status='eligible_if_policy_approved') risk_eligible_count,
 count(*) FILTER(WHERE proposed_interval_status='outside_proposed_risk_window') outside_risk_window_count,
 count(*) FILTER(WHERE proposed_interval_status='no_prior_observation') no_prior_count,
 count(*) FILTER(WHERE proposed_interval_status IN ('flagged_boundary','unexplained_or_unapproved_weekday_gap')) risk_excluded_issue_count
 FROM analytics.nav_intervals GROUP BY instrument_id
)
SELECT c.*,c.last_nav_date date_key,g.absent_weekdays,g.expected_closures,g.likely_legitimate_gaps,
 g.unresolved_gaps,v.risk_eligible_count,v.outside_risk_window_count,v.no_prior_count,v.risk_excluded_issue_count,
 CURRENT_TIMESTAMP dataset_query_timestamp,
 'Absent weekdays are not necessarily missing NAVs; equity historical calendar timing caveat'::text limitations,
 'Sharpe; Sortino; correlation; beta; tracking error; information ratio; benchmark excess return'::text suppressed_metrics
FROM coverage c JOIN gaps g USING(instrument_id) JOIN intervals v USING(instrument_id);

CREATE OR REPLACE VIEW analytics.pbi_source_lineage AS
SELECT DISTINCT n.instrument_id,n.ingestion_run_id,r.source_id,s.source_code,s.provider_name,s.source_url,
 r.retrieved_at,r.file_sha256,r.raw_file_path,r.pipeline_version,r.observed_start_date,r.observed_end_date,
 s.redistribution_status
FROM analytics.daily_nav n JOIN core.ingestion_run r USING(ingestion_run_id)
JOIN core.source s USING(source_id);
GRANT SELECT ON analytics.pbi_fund_overview,analytics.pbi_date,analytics.pbi_daily_performance,
 analytics.pbi_monthly_returns,analytics.pbi_calendar_year_returns,analytics.pbi_drawdowns,
 analytics.pbi_performance_snapshot,analytics.pbi_risk_snapshot,analytics.pbi_rolling_63,
 analytics.pbi_rolling_252,analytics.pbi_quality_summary,analytics.pbi_source_lineage TO ifa_app;
COMMIT;
