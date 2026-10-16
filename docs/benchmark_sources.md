# Benchmark integration and eligibility

Reviewed 7 October 2026. The two issuer-designated official index series are technically accessible without payment in the **Index Level** column of the already acquired DWS XLSX files. No new dataset was downloaded. They are official-index observations supplied by the fund issuer, not ETF proxies and not independently acquired index-administrator histories.

Detailed observation-derived table withheld pending permission; exact evidence is retained locally.

Identity/basis evidence: [equity issuer page](https://etf.dws.com/en/LU0380865021-euro-stoxx-50-ucits-etf-1c/) identifies the EUR NTR benchmark; [STOXX identifier table](https://stoxx.com/index/sx5t/?factsheet=true) distinguishes SX5T from the price and gross-return variants. [Bond issuer page](https://etf.dws.com/en/LU0290355717-eurozone-government-bond-ucits-etf-1c/) identifies the iBoxx benchmark; [DWS sovereign-index explanation](https://etf.dws.com/de-ch/wissen/angebotene-assetklassen/festverzinsliche-wertpapiere/staatsanleihen/) explains coupon reinvestment. That older educational page is used for return-basis evidence, not current fund replication/fees.

## Exact acquisition and loading

The existing requests were:

- [Equity export](https://etf.dws.com/api/pdp/de-de/etf/LU0380865021/historicaldata/download?startDate=2021-09-30&endDate=2026-09-30&includeTax=false).
- [Bond export](https://etf.dws.com/api/pdp/de-de/etf/LU0290355717/historicaldata/download?startDate=2021-09-30&endDate=2026-09-30&includeTax=false).

Raw paths, acquisition timestamps and checksums are retained as project provenance. Detailed populated benchmark coverage and observed missing-level dates are withheld in local evidence. Original date/basis flags and the unresolved alignment gate remain unchanged.

New core.benchmark metadata refers to index instruments 7 (bond) and 8 (equity); benchmark IDs 1 and 2, respectively. Sources remain S06/source ID 1 and S01/source ID 2. Original benchmark ingestion-run IDs are 7 and 8; repeat run IDs 9 and 10 insert **zero** observations. Assignments 1 and 2 are effective 2021-09-30 through 2026-09-30 and cannot overlap for the same fund. These are project mappings, not unsupported assertions about prospectus assignments before the documented project window. Benchmark observations retain the original export retrieval timestamps/checksums.

## Important unresolved consistency gate

**Neither benchmark is approved for relative-risk calculations yet.** Loaded benchmark observations remain flagged and date_alignment_status remains unverified. Private endpoint checks found equity discrepancies between issuer-displayed benchmark returns and the cached export ratios that exceed rounding. Exact benchmark values, comparative returns and numerical discrepancy magnitudes are withheld pending redistribution permission; verified pre-redaction details remain in the ignored local archive. No date shift or substitution was applied.

Different reporting boundaries, index versions/revisions, effective dates or source defects could explain discrepancies. None is asserted as fact. Do not choose a lag that maximizes correlation or silently shift the observations. A fund-issuer benchmark column does not independently verify date alignment. Resolve this against documented administrator data or issuer clarification before clearing the flags. This is a separate gate from the calendar-rule approval.

Direct administrator access was investigated through [STOXX end-of-day data](https://www.stoxx.com/end-of-the-day-data?eodd=2), historical file URLs and [S&P government index information](https://www.spglobal.com/spdji/en/index-family/fixed-income/europe-eurozone/government/). Those checks did not establish a usable independent no-cost five-year acquisition in this session; they do not prove that such access is impossible. A separate ETF proxy was not substituted merely to hide the discovered discrepancy. The official issuer-provided series is loaded as a reviewable candidate with explicit eligibility flags; a proxy remains an option if independent reconciliation fails.

Local reuse/redistribution restrictions remain those in the source register. Raw index data and local outputs are Git-ignored; the equity issuer explicitly restricts further dissemination of index information. No open-data license has been inferred. This report documents technical access and quality limitations.

## Reproduction

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m investment_fund_analytics.benchmark_loading
.\.venv\Scripts\python.exe -m pytest -q
```

Successful load attempts are retained, identical observations are preserved, and conflicts abort the transaction; failed attempts are not guaranteed a retained audit run. Load results are recorded locally in data/processed/benchmarks/load_validation.json.
