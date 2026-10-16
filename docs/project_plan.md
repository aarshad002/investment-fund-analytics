# Investment Fund Performance & Risk Analytics

Planning date: 7 October 2026. Status: design only; no implementation authorized by this document.

## Project objective and boundaries

Build a reproducible portfolio project that turns real public fund data into a documented performance and risk comparison, backed by Python, PostgreSQL, SQL, and Power BI. Demonstrate technical skill and sound financial interpretation for Data Analyst, Data Scientist, and Financial Data roles in Luxembourg.

The core deliverable is a trustworthy analytical workflow and dashboard. Machine learning is optional and must not delay the core project. All processing must run on a normal Windows laptop using CPU and local storage. No GPU, HPC, paid market-data dependency, or cloud service is required.

Initial target: 6–10 UCITS fund share classes across equity and bond categories, with approximately five years of daily observations where available. Prefer accumulating share classes and EUR-denominated analysis. Aim to include Luxembourg-domiciled funds if suitable public history is available; do not substitute domicile claims for verified metadata. Irish-domiciled UCITS ETFs may serve as clearly labelled proxies. This is a small selected sample, not a representation of the entire Luxembourg fund industry.

Exclude portfolio optimization, trading execution, investor-level returns, regulatory certification, full holdings attribution, and production infrastructure. Do not infer flows or fund assets from price movements.

## 1. Business problem

Fund performance is difficult to compare when returns, currencies, observation windows, distributions, and benchmarks differ. A high return alone does not show the volatility or losses an investor experienced.

The project will answer:

- Which funds delivered the strongest return within comparable categories and time periods?
- How much volatility, downside risk, and drawdown accompanied that return?
- How did each fund perform relative to a documented benchmark or investable proxy?
- How stable were performance and risk across rolling windows and stressed periods?
- Which observations or data limitations reduce confidence in a comparison?

Success means that a reviewer can trace dashboard values to SQL outputs, reproduce them locally, and understand the assumptions. Findings will be descriptive and educational, rather than investment recommendations or regulatory risk ratings.

## 2. Target users

| User | Decision or review need | Planned output |
| --- | --- | --- |
| Fund analyst or investment research analyst | Compare funds within meaningful peer groups | Performance and risk comparison with benchmark context |
| Risk analyst | Identify drawdowns, tail losses, and changing volatility | Risk page and rolling risk charts |
| Portfolio reporting or management team | Summarize results and explain changes clearly | Executive overview and fund detail page |
| Data analyst or data engineer | Assess data reliability and lineage | Quality report, database model, and reproducible pipeline |
| Luxembourg hiring manager | Evaluate SQL, Python, BI, and financial reasoning | Repository, dashboard, concise report, and demonstration |

Use ISIN and share-class identity as the financial anchors. Separate fund domicile, trading venue, share-class currency, underlying currency exposure, and currency hedging. English documentation is the default.

## 3. Data sources and selection strategy

### Proposed source hierarchy

| Data need | Preferred source | Use and constraints |
| --- | --- | --- |
| Fund identity and characteristics | Official issuer product pages, factsheets, and fund documents | Verify ISIN, name, domicile, asset class, accumulation/distribution policy, currency, hedging, benchmark, and ongoing charges; record document date |
| Daily fund history | Official issuer public historical NAV exports where available | Preferred for fund performance; verify downloadable coverage, return basis, and reuse terms for every selected share class |
| Price-history fallback | A public market-data provider with documented instrument coverage and permitted access | Use only after validating exchange, currency, adjustment conventions, coverage, and access restrictions; label market-price results explicitly |
| Benchmark history | Public official index history where accessible, otherwise a documented UCITS ETF proxy | Require compatible currency and price/total-return basis; a proxy is not the official index and has its own costs and tracking differences |
| EUR exchange rates | ECB reference rates / ECB Data Portal | Currency conversion with explicit quote direction and observation dates |
| EUR cash-rate proxy | ECB euro short-term rate (€STR) | Convert annual quoted rates into interval cash returns using the documented day-count convention; treat as a cash proxy rather than a guaranteed investor return |

Source references verified during planning:

- [iShares UCITS product page example](https://www.ishares.com/uk/individual/en/products/328658/ishares-s-p-500-equal-weight-ucits-etf): illustrates issuer metadata and NAV-based performance disclosures. It does not establish that every candidate has an accessible daily export.
- [ECB SDMX web services](https://data.ecb.europa.eu/help/getting-data-web-services-sdmx-0) and [API examples](https://data.ecb.europa.eu/help/api/data-examples): documented programmatic retrieval of statistical series.
- [ECB reference exchange rates](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html): official FX reference source, rather than executable dealing prices.
- [ECB €STR dataset](https://data.ecb.europa.eu/data/datasets/EST): proposed EUR cash-rate source.
- [Alpha Vantage documentation](https://www.alphavantage.co/documentation/): a provider candidate, not a committed dependency. Its daily adjusted endpoint is marked premium, so it cannot be assumed to satisfy the free-data requirement.

### Data feasibility gate

Before committing the universe, inspect one equity fund and one bond fund end to end. Confirm history availability, access method, permissions, units, dates, distributions, and adjustment basis. Expand only after those checks pass. Candidate fund names and exact identifiers remain to be selected; no source has yet been ingested or licensed for redistribution.

Select a fixed historical window ending at the latest complete month available across the chosen sample. Record exact start/end dates and acquisition timestamp. Prefer five years; reduce to at least three years or a smaller universe if needed, documenting the tradeoff. Do not pay for data to preserve the initial scope. If usable NAV histories cannot be obtained, use clearly identified UCITS ETF market-price analysis and rename the affected metrics accordingly.

Maintain a source register with URL, instrument identifier, method, retrieval time, observation coverage, checksum, terms/license reference, allowed redistribution, and known limitations. Public visibility is not permission to republish. Keep raw files local by default; publish acquisition instructions and results only where permitted.

### Planned ingestion and cleaning

Preserve original downloads in `data/raw/`. Python will parse files, standardize column names and dates, normalize identifiers and numeric formats, and write validated tables. Separate intermediate and analysis-ready outputs. Support manual official downloads when automated access is unsuitable; document each step so another user can repeat it.

Validate uniqueness, positive prices/NAVs, missing dates, currency consistency, observation ordering, coverage, duplicate conflicts, distributions, splits, and unusual return jumps. Flag outliers for investigation rather than deleting them automatically. Record rejected rows and reasons.

Use each instrument's actual observation calendar for native returns. Do not forward-fill missing fund prices into returns or treat missing observations as zero returns. Pairwise comparisons use aligned observations; multi-day gaps must be flagged or excluded from daily risk estimates. Any FX or cash-rate carry-forward must use an explicit age limit and avoid future observations. Show common-window and individual-history results separately.

## 4. Key KPIs and calculation conventions

Daily simple return: `r(t) = V(t) / V(t-1) - 1`, where V is a verified total-return index or an appropriately adjusted value series. Unadjusted distributing NAV requires distributions and a documented reinvestment convention. Without them, report price/NAV change and suppress total-return claims and dependent comparisons.

Use 252 observations per year for daily volatility annualization, explicitly labelled as an approximation. Use actual elapsed calendar years for CAGR. Returns are decimals in storage and percentages in presentation. Ratios are unitless. Return series, FX conversion, cash rates, and benchmarks must share a consistent reporting basis.

| KPI | Definition | Interpretation and safeguards |
| --- | --- | --- |
| Period cumulative return | Product of `(1 + r)` minus 1 over the selected valid window | Compound rather than sum returns |
| CAGR | `(ending wealth / starting wealth)^(1 / elapsed years) - 1` | Require at least one year; display shorter-window return without annualized growth |
| YTD and trailing 1/3/5-year return | Return from documented boundary observations to the as-of date | Require sufficient history; clearly distinguish cumulative and annualized multi-year figures |
| Monthly and calendar-year return | Compound valid observations within the period | Flag incomplete periods and missing coverage |
| Benchmark excess return | Fund cumulative return minus benchmark cumulative return over the same window | Percentage-point difference, not a compounded relative-wealth return |
| Sharpe ratio | Mean daily excess return / sample standard deviation of daily excess returns × square root of 252 | Use aligned interval cash returns; suppress when insufficient data or denominator is zero |
| Positive-month proportion | Positive complete months / valid complete months | Descriptive consistency measure, not a probability forecast |
| Ongoing charges | Latest documented issuer figure, with effective date | Context only; do not subtract again from net-of-fee NAV performance |
| Data coverage | Observed / expected observations using the documented calendar | Include history dates, valid count, stale-data status, and limitations |

For an EUR-per-unit value conversion, if ECB quotes q foreign-currency units per EUR, divide the foreign-currency value by q. Currency translation does not replicate a currency-hedged share class. Prefer EUR cash comparisons; suppress non-EUR Sharpe/Sortino ratios unless an appropriate matching cash-rate series is obtained.

Require at least 252 valid aligned daily observations for annualized risk and ratios, and 60 complete monthly observations for five-year comparisons. Record actual counts. Unsupported metrics remain null with an explanatory status, rather than zero.

## 5. Risk metrics

| Metric | Planned definition | Use and limitations |
| --- | --- | --- |
| Annualized volatility | Sample daily return standard deviation × square root of 252 | Historical dispersion; independence/stationarity assumptions limit interpretation |
| Drawdown | Wealth / running wealth peak minus 1 | Plot negative values through time |
| Maximum drawdown | Minimum drawdown over the window | Report as a negative percentage with peak/trough dates |
| Recovery duration | Time from prior peak until wealth reaches that peak again | Report unrecovered episodes as ongoing, not zero days |
| Downside deviation | Square root of mean squared negative deviations from interval cash-return target × square root of 252 | Mean over all valid observations, with target documented |
| Sortino ratio | Annualized mean daily excess return / annualized downside deviation | Suppress if downside deviation is zero or coverage is insufficient |
| Historical 95% VaR | Negative of the empirical 5th-percentile daily return | One-day return-loss threshold; specify quantile method and retain signed result |
| Historical 95% expected shortfall | Negative mean of returns at or below the VaR return cutoff | Tail mean, with tie handling and tail observation count disclosed |
| Tracking error | Sample standard deviation of fund-minus-benchmark daily returns × square root of 252 | Only for aligned, comparable series |
| Information ratio | Mean daily active return / its sample standard deviation × square root of 252 | Requires a suitable benchmark and nonzero denominator |
| Beta and correlation | Covariance with benchmark / benchmark variance; Pearson return correlation | Descriptive historical relationship; not causal exposure proof |
| Rolling risk | 63-day and 252-day volatility, plus 252-day Sharpe where supported | Full windows only; disclose window sizes |

VaR and expected shortfall describe observed history and can underestimate unseen losses. They are not regulatory capital measures, guarantees, or formal UCITS risk categories. Stress views will use predeclared dates within available history and show drawdown, return, and volatility without claiming causal attribution. Peer rankings must stay within comparable asset classes and common windows.

## 6. Database design

Use a single local PostgreSQL database with three logical schemas: `staging` for parsed source records, `core` for validated entities and observations, and `analytics` for derived tables/views. Design for tens of thousands of daily rows, not distributed processing.

| Table or view | Grain / proposed key | Main fields and relationships |
| --- | --- | --- |
| `core.fund_share_class` | One share class; surrogate ID, unique verified ISIN | Name, issuer, domicile, category, currency, distribution policy, hedging, inception date |
| `core.instrument` | One measurable NAV, listing, index, or proxy series; instrument ID | Type, share-class ID where applicable, ticker/venue, currency, value/return basis; one share class may have multiple listings |
| `core.benchmark_assignment` | One fund/benchmark assignment per effective interval | Fund instrument, benchmark instrument, start/end, rationale; prevent overlapping assignments |
| `core.fund_metadata_snapshot` | Share class and effective date | Charges and other time-varying facts with source reference; avoid treating current metadata as historical truth |
| `core.source` | One provider/source definition | URL, method, terms reference, dataset identity |
| `core.ingestion_run` | One acquisition/run ID | Timestamp, file checksum, status, row counts, source ID, pipeline version |
| `core.observation` | Instrument, observation date, value basis | Value, currency, ingestion-run ID, quality status; prohibit conflicting duplicate keys |
| `core.distribution` | Instrument, ex-date, event ID | Cash amount, currency, payment date if available, source; needed only for suitable distributing series |
| `core.fx_rate` | Date and currency pair | Rate, quote direction, source/run ID |
| `core.cash_rate` | Series and reference date | Annual rate, publication date, day count, source/run ID |
| `core.quality_issue` | One issue ID | Run/instrument/date, check, severity, details, resolution |
| `analytics.daily_return` | Instrument, date, reporting currency, return basis | Return, interval length, benchmark/cash return where aligned, validity status |
| `analytics.metric_snapshot` | Instrument, as-of date, window, currency, basis, methodology version | Metric values, valid counts, window boundaries, status, source lineage |
| `analytics` dashboard views | Documented grain for each view | Fund overview, monthly performance, rolling risk, drawdowns, and quality summaries |

Use foreign keys, date types, appropriate numeric precision, positive-value checks, and indexes on instrument/date. Re-runs must be idempotent: duplicate downloads cannot double-count observations. Keep rejected rows in staging or a rejection report. Corrections must retain acquisition lineage and a clear version policy.

SQL analysis will demonstrate joins, CTEs, `LAG`, window functions, grouped monthly results, common-window peer rankings, benchmark comparisons, and quality checks. Python will handle numerical routines where that improves clarity. Reconcile selected independently calculated SQL and Python results within documented tolerance.

Power BI will import a small star-shaped analytical model with fund/instrument and date dimensions and clearly grained daily, monthly, and metric facts. Avoid ambiguous many-to-many joins and snapshot double-counting. Precomputed metric snapshots support defined window selections; arbitrary dashboard date selections must not silently reuse mismatched KPIs. Use SQL as the default analytical source and document any DAX measures.

## 7. Dashboard pages

| Page | Main content | User interaction |
| --- | --- | --- |
| Executive overview | Selected-universe count, period return, volatility, drawdown, data as-of date, peer table | Category, fund, reporting currency, and predefined window filters |
| Performance comparison | Rebased wealth starting at 100, monthly return heatmap, calendar-year comparison, benchmark excess return | Compare a small number of funds on a common window |
| Risk and drawdowns | Return/volatility scatter, drawdown chart, rolling volatility, VaR/ES table, recovery status | Category and risk window filters; tooltips explain units and assumptions |
| Fund detail | Identity, domicile, currency, charges date, benchmark/proxy, individual performance and risk | Drill-through from fund tables |
| Data quality and methodology | Coverage, missing intervals, flagged observations, refresh status, source links and definitions | Review affected funds and explanation of suppressed metrics |

Use consistent colors, readable labels, accessible contrast, and explicit units. Show EUR-converted or native-currency status and NAV/market-price/total-return basis on each relevant visual. Disable cross-category league tables by default. Risk charts and KPI cards must respect the same window and valid sample. The optional ML component may be summarized in the report; a sixth dashboard page is only added if it improves interpretation.

## 8. Optional lightweight ML component

Proposed experiment: predict next-month realized volatility for each sufficiently observed fund, using recent volatility, downside deviation, drawdown, and past returns. This demonstrates supervised learning and time-aware evaluation without making buy/sell recommendations.

- Target: sample daily volatility in the next complete calendar month, annualized with the same convention as the core analysis.
- Features: information available by month-end only. Verify publication timing and exclude forward-looking observations or revised metadata that would leak future information.
- Baseline: predict that next-month volatility equals the latest month's volatility.
- Model: regularized linear regression with scikit-learn; an optional small tree model only if justified. Avoid deep learning and broad hyperparameter searches.
- Validation: chronological expanding-window evaluation, with a final untouched time block shared across all funds. Purge training labels whose observation windows overlap validation/test boundaries. Fit scaling and tuning only on training folds.
- Evaluation: MAE in volatility percentage points, per-fund errors, comparison with baseline, and stability across time blocks. Explain sample size and dependence among related funds.
- Decision gate: include only after the core project is complete and adequate labelled months exist. A baseline-beating result is not required; report weak or negative findings honestly. Drop ML if the sample cannot support a credible evaluation.

## 9. Project phases and acceptance criteria

Indicative effort: 5–7 part-time weeks for the core project, plus up to one week for optional ML. This is an estimate, not a deadline. Data feasibility determines the final scope.

| Phase | Planned work | Exit criterion |
| --- | --- | --- |
| 0. Scope and data feasibility | Inspect candidate sources, validate two sample histories, fix fund universe/window and return basis | Source register and a viable no-cost dataset; limitations recorded |
| 1. Local environment and specification | Document tested Python/PostgreSQL/Power BI versions, configuration, data dictionary, ER diagram, and metric definitions | Another user can follow setup instructions; no secrets committed |
| 2. Ingestion and cleaning | Acquire real data, preserve raw files, standardize, validate, and produce quality report | Traceable cleaned observations with duplicates resolved and gaps explained |
| 3. PostgreSQL and SQL | Create schema, load data, build analytical queries/views, verify idempotent loading | Keys/constraints pass and repeat loading leaves stable counts |
| 4. Performance and risk analysis | Compute metrics, benchmark comparisons, rolling windows, and documented stress views | Hand-check representative periods; reconcile SQL/Python; unsupported metrics suppressed |
| 5. Power BI dashboard | Build model, measures, visuals, tooltips, and filter behavior | Dashboard values reconcile to analytical outputs; filters and units behave consistently |
| 6. Optional ML | Run baseline and small model with chronological validation | Transparent held-out evaluation and leakage audit, or documented omission |
| 7. Portfolio packaging | Write findings, limitations, reproducibility guide, dashboard exports, and repository narrative | Clean local reproduction and reviewer-ready deliverables |

### Reproducibility and verification requirements

Document local installation and startup for PostgreSQL and Power BI Desktop, database creation and least-privilege project user, virtual environment setup, and dependency versions tested on Windows. Provide a future `.env.example` containing placeholders only; do not write configuration or pipeline code during this planning stage.

The eventual guide must specify acquisition, cleaning, database loading, SQL analysis, metric generation, and dashboard refresh order. A cached raw-data path should support repeat runs offline after acquisition. Fresh acquisition still depends on provider access, and Power BI refresh requires the documented local connection/driver. Docker and cloud accounts are not prerequisites.

Keep small input files and CPU-only operations. Record run time, row counts, and approximate memory use on the development laptop. Pin tested dependencies when implemented, record database/Power BI versions, and capture Git revision, source checksums, observation cutoff, parameters, and random seeds where applicable.

Verify a constant-value example, a known return sequence, a peak/trough/recovery sequence, currency conversion direction, and benchmark alignment. These are future calculation checks; published findings must use real data. Check sample standard deviation conventions, distribution handling, date boundaries, absent history, and zero denominators. Finally reproduce from documented inputs and reconcile dashboard cards to SQL results.

### Main risks and responses

| Risk | Response |
| --- | --- |
| Fund history unavailable or restricted | Reduce universe, use permitted manual downloads, or label an ETF price-history fallback |
| Distributions or adjustment methodology unclear | Prefer accumulating classes; suppress total-return metrics until verified |
| Benchmark data unavailable | Use a justified investable proxy and disclose the distinction |
| Short history or survivorship bias | Report selection criteria and coverage; avoid industry-wide claims |
| Mixed currencies or mismatched calendars | Enforce explicit conversion and aligned-window policies |
| Excess scope | Deliver ingestion, SQL, metrics, and dashboard first; defer ML and extra pages |
| Restricted redistribution | Publish methodology and permitted artifacts rather than raw licensed files |

## 10. Final portfolio deliverables

1. Professional GitHub repository with README, scope, directory guide, dependency versions, and complete Windows reproduction instructions.
2. Source register, data dictionary, quality report, and documented fund selection and observation window in `docs/`.
3. Python ingestion/cleaning and metric workflow in `src/`, with focused verification and explanatory notebooks rather than notebook-only logic.
4. PostgreSQL schema, ER diagram, repeatable loading instructions, and readable analytical SQL in `sql/`.
5. Documented performance and risk outputs, with selected matplotlib figures and an explicit methodology/version record.
6. Power BI dashboard with five core pages, local refresh instructions, screenshots, and PDF exports. The current `.gitignore` excludes PBIX/PBIT files and generated reports; deliberately review artifact tracking or use permitted GitHub release assets during packaging so deliverables are actually accessible.
7. A concise findings report describing business questions, evidence, interpretation, limitations, and further work. Do not invent findings in advance.
8. Optional ML experiment with baseline, feature/target definitions, temporal evaluation, errors, and limitations; clearly state if omitted.
9. A short walkthrough or presentation showing the data-to-dashboard flow and one traceable fund comparison suitable for interviews.

Completion requires usable public-data provenance, validated financial calculations, SQL-backed dashboard results, a repeatable local workflow, and a clear explanation of limitations. ML is not a completion requirement.
