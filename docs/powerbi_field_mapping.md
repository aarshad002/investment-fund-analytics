# Power BI field mapping

Import/rename views exactly as [data model](powerbi_data_model.md). Hide instrument IDs and technical keys from the report field picker after relationships are configured. Disable automatic date hierarchies. Keep methodological/status fields accessible in tooltips. DAX: [measures.dax](../powerbi/measures.dax), one definition at a time; these measures select approved SQL results and prevent aggregation across incomparable instruments.

| Fields / measures | Type and format | Usage / aggregation |
| --- | --- | --- |
| DimFund instrument_id; all fact IDs | Whole number | Keys; Don't summarize; hidden |
| DimFund ISIN, name, issuer, category, domicile, currency, income policy, benchmark name | Text | Slicers/detail; benchmark metadata only |
| DimDate date_key; every date_key/start/end/boundary/peak/trough/recovery | Date; yyyy-MM-dd | Continuous date axes or detail; no sum |
| DimDate calendar_year/month_number/quarter/weekday_number | Whole number | Sort/group; Don't summarize |
| DimDate month_name/year_month | Text | Sort month_name by month_number; year_month chronologically by month_start |
| NAV; nav/running_peak | Decimal number; 0.0000 EUR | One instrument/date; no totals |
| Rebased NAV | Decimal number; 0.00 | Index base 100 on stored base_date; never called freshly rebased selected window |
| Cumulative NAV Return, CAGR, Maximum Drawdown | Decimal number; 0.00% | One fund/fixed performance window; no averaging/summing |
| Annualized Volatility, Downside Deviation Zero Target, Historical VaR 95, Historical ES 95 | Decimal number; 0.00% | One fund/controlled-risk window; downside zero target; VaR/ES valuation interval |
| Latest Rolling 63/252; Rolling 63/252 Volatility | Decimal number; 0.00% | Latest cards fixed snapshot; charts per date |
| Monthly NAV Return / Calendar Year NAV Return | Decimal number; +0.00%;-0.00%;0.00% | No matrix/bar totals; null remains blank |
| Cumulative Series / Observed Drawdown | Decimal number; 0.00% | One instrument/date; drawdown negative |
| observations, valid_count, tail_count, count_63/252, calendar gap counts | Whole number; 0 | Actual sample counts; never percent |
| interval_days, recovery_duration_days, ongoing_duration_days | Whole number; 0 | Calendar-day duration, not observation count |
| source_id/run IDs, SHA-256, source_url, raw_file_path, pipeline_version | ID/text | Lineage table only; URL data category Web URL where appropriate |
| retrieved_at, dataset_query_timestamp | Date/time | Original acquisition vs database query; convert UTC explicitly in Power Query |
| RefreshInfo refreshed_at_utc | Date/time; yyyy-MM-dd HH:mm:ss | Model refresh UTC, disconnected one-row table |
| status, recovery_status, limitations, suppressed_metrics | Text | Visible explanatory labels/tooltips; never convert to zero |
| annualization_intervals, downside_target | Whole/decimal | Fixed methodology fields 252 and zero; no ratio metric is enabled |

DAX is needed for visual-context safety, single-fund cards, labels and model refresh display. Financial formulas stay in PostgreSQL; no DAX compounding, volatility, tail estimation, benchmark subtraction or ratio calculation is required. The monthly heatmap uses DimDate[calendar_year] rows, DimDate[month_name] columns and Monthly NAV Return values; explicitly turn off totals, since these measures deliberately yield blank where the grain is not unique. Tooltips must include period status and actual boundaries. Do not display partial_or_observed_return as the complete monthly/year return.

All six disabled risk metrics plus benchmark excess return are listed on the methodology page. Benchmark fields remain text only; no benchmark-index fact is imported.
