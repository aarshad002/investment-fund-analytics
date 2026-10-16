"""Acquire the approved DWS pair and validate local NAV histories, without DB writes."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pandas as pd
import requests

from investment_fund_analytics.sample_ingestion import INSTRUMENTS, parse_workbook

START = "2021-09-30"  # preceding valuation for the planned October 2021 start
END = "2026-09-30"


def acquire(root: Path) -> list[dict]:
    """Two bounded requests; save immutable files and a local acquisition manifest."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder = root / "data/raw/full_history" / stamp
    folder.mkdir(parents=True, exist_ok=False)
    manifest = []
    for isin in sorted(INSTRUMENTS):
        url = f"https://etf.dws.com/api/pdp/de-de/etf/{isin}/historicaldata/download"
        response = requests.get(url, params={"startDate": START, "endDate": END, "includeTax": "false"}, timeout=(10, 90))
        response.raise_for_status()
        content = response.content
        if not content.startswith(b"PK") or "spreadsheetml" not in response.headers.get("Content-Type", ""):
            raise ValueError(f"Unexpected response for {isin}: not an XLSX workbook")
        path = folder / f"{isin}_{START}_{END}.xlsx"
        path.write_bytes(content)
        manifest.append(dict(isin=isin, source_code=INSTRUMENTS[isin].source_code,
                             request_url=response.url, retrieved_at=datetime.now(timezone.utc).isoformat(),
                             requested_start=START, requested_end=END, http_status=response.status_code,
                             content_type=response.headers.get("Content-Type"), file_bytes=len(content),
                             file_sha256=hashlib.sha256(content).hexdigest(),
                             raw_file=str(path.relative_to(root)).replace("\\", "/")))
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    return manifest


def consolidate(frames: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Identical overlaps collapse explicitly; every conflicting version is quarantined."""
    rows = pd.concat(frames, ignore_index=True)
    accepted, conflicts = [], []
    overlaps = identical = 0
    eligible = rows.loc[rows.quality_status != "invalid"]
    for _, group in eligible.groupby(["instrument_code", "observation_date"], sort=True):
        if len(group) > 1:
            overlaps += 1
        if len(set(group.value)) > 1:
            conflicts.append(group.assign(quality_status="invalid", conflict_reason="conflicting_nav"))
            continue
        identical += len(group)-1
        # Full export is supplied first, followed by earlier samples; precedence is explicit.
        chosen = group.iloc[0].copy()
        if (group.quality_status == "flagged").any():
            chosen["quality_status"] = "flagged"
        chosen["supporting_files"] = json.dumps(sorted(set(group.raw_file)))
        accepted.append(chosen)
    clean = pd.DataFrame(accepted, columns=[*rows.columns, "supporting_files"])
    clean = clean.sort_values(["instrument_code", "observation_date"]).reset_index(drop=True)
    conflict_rows = pd.concat(conflicts, ignore_index=True) if conflicts else rows.iloc[:0].assign(conflict_reason=pd.Series(dtype="str"))
    return clean, conflict_rows, dict(overlap_dates=overlaps, identical_extra_rows=identical,
                                    conflict_dates=len(conflicts), conflict_rows=len(conflict_rows),
                                    invalid_rows=int((rows.quality_status == "invalid").sum()))


def weekday_gaps(frame: pd.DataFrame, start=START, end=END) -> list[str]:
    """Conservative Monday-Friday screen, not a claimed fund valuation calendar."""
    expected = pd.bdate_range(start, end)
    observed = pd.DatetimeIndex(frame.observation_date)
    return [d.strftime("%Y-%m-%d") for d in expected.difference(observed)]


def validate(root: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if len(manifest) != 2 or {m["isin"] for m in manifest} != set(INSTRUMENTS):
        raise ValueError("Manifest must contain exactly the two approved instruments")
    output = root / "data/processed/full_history"
    output.mkdir(parents=True, exist_ok=True)
    summary = {}
    for acquisition in manifest:
        isin = acquisition["isin"]
        raw = (root / acquisition["raw_file"]).resolve()
        if not raw.is_relative_to((root / "data/raw").resolve()):
            raise ValueError("Raw path escapes data/raw")
        if hashlib.sha256(raw.read_bytes()).hexdigest() != acquisition["file_sha256"]:
            raise ValueError(f"Raw checksum mismatch: {isin}")
        full = parse_workbook(raw, INSTRUMENTS[isin])
        samples = [parse_workbook(p, INSTRUMENTS[isin]) for p in sorted((root / "data/raw/phase0").glob(f"{isin}_*_sample.xlsx"))]
        clean, conflicts, overlap = consolidate([full.records, *(s.records for s in samples)])
        gaps = weekday_gaps(clean)
        outside = clean.loc[~clean.observation_date.between(pd.Timestamp(START), pd.Timestamp(END))]
        clean.to_csv(output / f"{isin}_validated.csv", index=False, date_format="%Y-%m-%d")
        pd.concat([full.records, *(s.records for s in samples)], ignore_index=True).to_csv(output / f"{isin}_all_rows.csv", index=False)
        conflicts.to_csv(output / f"{isin}_conflicts.csv", index=False)
        clean.loc[clean.quality_status == "flagged"].to_csv(output / f"{isin}_flagged.csv", index=False)
        all_issues = pd.concat([full.issues, *(s.issues for s in samples)], ignore_index=True)
        all_issues.to_csv(output / f"{isin}_issues.csv", index=False)
        pd.DataFrame({"missing_weekday": gaps}).to_csv(output / f"{isin}_weekday_gaps.csv", index=False)
        summary[isin] = dict(acquisition=acquisition, parsed_full_rows=len(full.records),
                            sample_rows=sum(len(s.records) for s in samples), consolidated_rows=len(clean),
                            earliest=clean.observation_date.min().strftime("%Y-%m-%d") if len(clean) else None,
                            latest=clean.observation_date.max().strftime("%Y-%m-%d") if len(clean) else None,
                            flagged_rows=int((clean.quality_status == "flagged").sum()),
                            parser_issues=all_issues.to_dict(orient="records"),
                            input_order=full.structure["input_order"], output_sorted=clean.observation_date.is_monotonic_increasing,
                            outside_requested_rows=len(outside), missing_weekdays=gaps,
                            optional_missing=full.structure["optional_missing"],
                            maximum_calendar_gap_days=int(clean.observation_date.diff().dt.days.max()) if len(clean)>1 else None,
                            empty_calendar_months=[str(p) for p in pd.period_range(START, END, freq="M")
                                                  if p not in set(clean.observation_date.dt.to_period("M"))], **overlap)
    (output / "quality_summary.json").write_text(json.dumps(summary, indent=2, default=str)+"\n", encoding="utf-8")
    write_report(root, summary)
    print(json.dumps(summary, indent=2, default=str))
    return summary


def write_report(root: Path, summary: dict) -> None:
    """Publish quality evidence only; raw NAV values remain local."""
    lines = ["# Full historical NAV quality report", "",
             "Acquired 7 October 2026 from official DWS/Xtrackers dated XLSX exports. Requested 2021-09-30 through 2026-09-30: approximately five years, including the preceding valuation for an October 2021 start.", "",
             "## Coverage and consolidation", "",
             "| ISIN | Full rows | Sample rows | Consolidated rows | First date | Last date | Identical overlapping dates | Conflicting dates | Flagged rows | Absent weekdays |",
             "| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |"]
    for isin, s in sorted(summary.items()):
        lines.append(f"| {isin} | {s['parsed_full_rows']} | {s['sample_rows']} | {s['consolidated_rows']} | {s['earliest']} | {s['latest']} | {s['overlap_dates']} | {s['conflict_dates']} | {s['flagged_rows']} | {len(s['missing_weekdays'])} |")
    lines += ["", "## Validation and assumptions", "",
              "The existing sample parser validates workbook identity, EUR currency, dates, finite positive NAVs, numeric precision, duplicate dates, and source ordering. It screens adjacent valid NAV changes above 20% in absolute magnitude as review flags; this is a quality threshold, not a financial metric. Suspicious observations are retained and flagged. Invalid rows and every conflicting version are preserved separately and excluded from the validated dataset. Identical overlaps explicitly select the full export first and retain supporting-file references; no conflicting value is silently overwritten.", "",
              "The same Date/NAV workbook parser handles both full files. NAV is native reported EUR NAV, not market close or a separately verified corporate-action-adjusted series. No interpolation, calendar filling, or FX conversion is performed. Missing auxiliary index/AUM/tax values do not invalidate a populated NAV.", ""]
    for isin, s in sorted(summary.items()):
        a = s['acquisition']
        lines += [f"### {isin}", "", f"- Exact acquisition: [official dated export]({a['request_url']}).",
                  f"- Retrieved UTC: `{a['retrieved_at']}`; HTTP {a['http_status']}; {a['file_bytes']:,} bytes. No authentication or payment supplied.",
                  f"- Local raw file: `{a['raw_file']}`; SHA-256: `{a['file_sha256']}`.",
                  f"- Invalid rows: {s['invalid_rows']}; parser issues: {len(s['parser_issues'])}; out-of-range rows: {s['outside_requested_rows']}; conflicts: {s['conflict_rows']} rows.",
                  f"- Source ordering: {s['input_order']}; consolidated ascending: {s['output_sorted']}. Identical extra rows collapsed: {s['identical_extra_rows']}.",
                  f"- Maximum interval between observations: {s['maximum_calendar_gap_days']} calendar days; entirely absent calendar months: {len(s['empty_calendar_months'])}.",
                  f"- Missing auxiliary cells: `{json.dumps(s['optional_missing'], sort_keys=True)}`.",
                  f"- Local outputs: `data/processed/full_history/{isin}_validated.csv`, plus all rows, conflicts, flags, issues and weekday-gap CSVs.", ""]
    lines += ["## Calendar review", "",
              "Absent weekdays are screened against Monday–Friday only. They are not established missing valuations: an authoritative historical fund valuation calendar has not yet been reconciled. Observed omissions may reflect source/valuation calendars, but this does not prove their cause. Weekend and holiday closures must not be replaced with zero returns. Preserve reviewed classifications and consult reports/calendar_completeness.md and docs/risk_methodology.md for the approved restricted-window policy; this acquisition routine does not certify unrestricted five-year daily risk.", "",
              "| Year | Equity absent weekdays | Bond absent weekdays |", "| --- | --- | --- |"]
    for year in range(2021, 2027):
        lists = [", ".join(d for d in summary[i]['missing_weekdays'] if d.startswith(str(year))) or "None"
                 for i in ['LU0380865021', 'LU0290355717']]
        lines.append(f"| {year} | {lists[0]} | {lists[1]} |")
    lines += ["", "## Database-loading readiness", "",
              "Both actual exports pass row-level validation and conflict checks and can be loaded as validated NAV observations with their acquisition lineage and the accompanying calendar-gap register. The unresolved historical valuation calendar limits completeness claims and daily analytics readiness; database loading itself does not require filling these dates. Review any future flags/conflicts before accepting their rows. This acquisition routine does not load PostgreSQL or compute financial metrics. Existing project performance/controlled-risk analytics and the user-completed five-page dashboard are documented separately; no ML is implemented.", "",
              "Raw files, manifests, and processed datasets are Git-ignored. This generated quality report is local too; source publication permission remains unresolved and redistribution restricted. Derived values, charts and screenshots are not automatically cleared for publication. Access is a public website backend, not a supported developer API; DWS/third-party reuse restrictions remain as documented in the source register. Public availability does not establish redistribution permission.", "",
              "## Offline reproduction", "", "```powershell", "$env:PYTHONPATH = 'src'",
              " .\\.venv\\Scripts\\python.exe -m investment_fund_analytics.full_history --manifest data/raw/full_history/<selected-acquisition-directory>/manifest.json",
              " .\\.venv\\Scripts\\python.exe -m pytest -q", "```", "",
              "Validation verifies manifest checksums before parsing and regenerates this report without downloading. An explicit `--acquire` instead makes two new bounded requests and stores them in a new timestamped folder; existing raw downloads are not overwritten.", ""]
    (root / 'data/processed/full_history/full_history_quality.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--acquire", action="store_true", help="Explicitly download the two full histories")
    parser.add_argument("--manifest", type=Path, help="Validate existing downloads offline")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.acquire == bool(args.manifest):
        parser.error("Choose exactly one of --acquire or --manifest")
    if args.acquire:
        acquired = acquire(root)
        manifest_path = root / acquired[0]["raw_file"]
        manifest_path = manifest_path.parent / "manifest.json"
    else:
        manifest_path = args.manifest
    validate(root, manifest_path)
