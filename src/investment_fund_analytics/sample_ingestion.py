"""Parse local DWS NAV workbooks; no network, database, or financial analytics."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib
import math

import pandas as pd
from openpyxl import load_workbook


@dataclass(frozen=True)
class InstrumentMetadata:
    isin: str
    fund_name: str
    source_code: str
    currency: str = "EUR"

    @property
    def instrument_code(self) -> str:
        return f"{self.isin}:NAV:{self.currency}:NATIVE"


INSTRUMENTS = {
    "LU0380865021": InstrumentMetadata("LU0380865021", "Xtrackers Euro Stoxx 50 UCITS ETF 1C", "S01"),
    "LU0290355717": InstrumentMetadata("LU0290355717", "Xtrackers II Eurozone Government Bond UCITS ETF 1C", "S06"),
}
MISSING = {"", "N/A", "NA", "NULL"}
RECORD_COLUMNS = ["isin", "fund_name", "instrument_code", "source_code", "currency",
                  "value_basis", "adjustment_status", "observation_date", "value",
                  "raw_date", "raw_value", "raw_file", "file_sha256", "sheet_name",
                  "raw_row_number", "quality_status"]
ISSUE_COLUMNS = ["raw_row_number", "check_code", "severity", "details"]


class WorkbookStructureError(ValueError):
    """Workbook cannot be interpreted safely as a single NAV table."""


@dataclass
class ParseResult:
    records: pd.DataFrame
    issues: pd.DataFrame
    structure: dict

    @property
    def clean(self) -> pd.DataFrame:
        """Structurally valid rows, including suspicious rows marked flagged."""
        return self.records.loc[self.records.quality_status != "invalid"].copy()


def _missing(value) -> bool:
    return value is None or (isinstance(value, str) and value.strip().upper() in MISSING)


def _date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value.strip(), "%d.%m.%Y").date()
        except ValueError:
            pass
    return None  # Numeric Excel serials without date formatting are not guessed.


def parse_workbook(path: str | Path, expected: InstrumentMetadata,
                   extreme_change_threshold: float = 0.20) -> ParseResult:
    """Retain all candidate rows; quarantine errors and flag >20% adjacent jumps.

    The jump is a validation heuristic, never persisted as a return metric.
    Duplicate-date groups are all quarantined, even when values are identical.
    """
    if not math.isfinite(extreme_change_threshold) or extreme_change_threshold <= 0:
        raise ValueError("Extreme-change threshold must be finite and positive")
    path = Path(path)
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    workbook = load_workbook(path, read_only=True, data_only=False)
    try:
        tables = []
        for sheet in workbook:
            rows = list(sheet.iter_rows(values_only=True))
            for index, row in enumerate(rows):
                names = [str(v).strip() if v is not None else "" for v in row]
                if "Date" in names and "NAV" in names:
                    if names.count("Date") != 1 or names.count("NAV") != 1:
                        raise WorkbookStructureError("Ambiguous Date/NAV columns")
                    tables.append((sheet.title, rows, index, names))
        if len(tables) != 1:
            raise WorkbookStructureError(f"Expected one Date/NAV table, found {len(tables)}")
        sheet_name, rows, header_index, names = tables[0]
        metadata = {}
        for row in rows[:header_index]:
            if row and row[0] in ("Name", "ISIN", "Currency", "As of"):
                key = row[0]
                if key in metadata:
                    raise WorkbookStructureError(f"Duplicate metadata label: {key}")
                metadata[key] = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ""
        if not all(metadata.get(key) for key in ("Name", "ISIN", "Currency", "As of")):
            raise WorkbookStructureError("Missing required identity metadata")
        date_column, nav_column = names.index("Date"), names.index("NAV")
        records, issues = [], []

        def issue(row_number, code, severity, details):
            issues.append(dict(raw_row_number=row_number, check_code=code,
                               severity=severity, details=details))

        file_errors = []
        if metadata["ISIN"] != expected.isin:
            file_errors.append("identity_mismatch")
            issue(None, "identity_mismatch", "error", "Workbook ISIN differs from expected instrument")
        if metadata["Currency"] != expected.currency:
            file_errors.append("unexpected_currency")
            issue(None, "unexpected_currency", "error", f"Expected {expected.currency}; found {metadata['Currency']}")
        for index in range(header_index + 1, len(rows)):
            row = rows[index]
            if all(v is None or v == "" for v in row):
                continue
            row_number = index + 1
            raw_date, raw_value = row[date_column], row[nav_column]
            parsed_date = _date(raw_date)
            invalid = bool(file_errors)
            if parsed_date is None:
                invalid = True
                issue(row_number, "missing_date" if _missing(raw_date) else "invalid_date", "error", "Expected DD.MM.YYYY or an Excel date cell")
            numeric = None
            if _missing(raw_value):
                invalid = True
                issue(row_number, "missing_nav", "error", "NAV is missing")
            else:
                try:
                    if isinstance(raw_value, bool):
                        raise InvalidOperation
                    numeric = Decimal(str(raw_value).strip())
                    if not numeric.is_finite():
                        raise InvalidOperation
                    if numeric <= 0:
                        invalid = True
                        issue(row_number, "nonpositive_nav", "error", "NAV must be positive")
                    elif numeric >= Decimal("10000000000") or numeric != numeric.quantize(Decimal("0.0000000001")):
                        invalid = True
                        issue(row_number, "numeric_precision", "error", "NAV cannot fit numeric(20,10) without rounding")
                except (InvalidOperation, ValueError):
                    numeric = None
                    invalid = True
                    issue(row_number, "invalid_numeric", "error", "NAV must be a finite decimal number")
            records.append(dict(isin=expected.isin, fund_name=expected.fund_name,
                                instrument_code=expected.instrument_code, source_code=expected.source_code,
                                currency=metadata["Currency"], value_basis="nav", adjustment_status="native",
                                observation_date=parsed_date, value=numeric,
                                raw_date=raw_date, raw_value=raw_value, raw_file=path.name,
                                file_sha256=checksum, sheet_name=sheet_name, raw_row_number=row_number,
                                quality_status="invalid" if invalid else "valid"))
        frame = pd.DataFrame(records, columns=RECORD_COLUMNS)
        frame["observation_date"] = pd.to_datetime(frame["observation_date"], errors="coerce")
        dates = frame.observation_date.dropna()
        order = "ascending" if dates.is_monotonic_increasing else "descending" if dates.is_monotonic_decreasing else "unordered"
        if order == "unordered":
            issue(None, "unordered_dates", "warning", "Input dates unordered; output sorted ascending")
        duplicates = frame.observation_date.notna() & frame.duplicated(["instrument_code", "observation_date"], keep=False)
        for index in frame.index[duplicates]:
            frame.loc[index, "quality_status"] = "invalid"
            issue(int(frame.loc[index, "raw_row_number"]), "duplicate_date", "error", "All rows for duplicated instrument/date quarantined")
        frame = frame.sort_values(["observation_date", "raw_row_number"], na_position="last").reset_index(drop=True)
        # Compare only adjacent valid rows in this file, never across separated samples or errors.
        for index in range(1, len(frame)):
            previous, current = frame.iloc[index - 1], frame.iloc[index]
            if previous.quality_status != "invalid" and current.quality_status != "invalid":
                change = abs(current.value / previous.value - 1)
                if change > Decimal(str(extreme_change_threshold)):
                    frame.loc[index, "quality_status"] = "flagged"
                    issue(int(current.raw_row_number), "extreme_change", "warning", f"Adjacent NAV jump exceeds {extreme_change_threshold:.0%}; retained for review")
        optional_missing = {}
        for column in ("Asset Under Management", "Index Level", "Interim Profits"):
            if column in names:
                position = names.index(column)
                optional_missing[column] = sum(_missing(rows[int(n)-1][position]) for n in frame.raw_row_number)
        return ParseResult(frame, pd.DataFrame(issues, columns=ISSUE_COLUMNS),
                           dict(sheet_names=workbook.sheetnames, table_sheet=sheet_name,
                                header_row=header_index+1, columns=[n for n in names if n],
                                metadata=metadata, input_order=order, optional_missing=optional_missing,
                                extreme_change_threshold=extreme_change_threshold))
    finally:
        workbook.close()


def run_samples(root: Path) -> None:
    """Process exactly the six approved local files and write reproducible artifacts."""
    output = root / "data/processed/phase0"
    output.mkdir(parents=True, exist_ok=True)
    lines = ["# Phase 0 sample quality report", "", "Generated by the local Phase 2 sample parser. No network requests or database writes.", "",
             "## Actual workbook structure", "", "All six files have one sheet named by ISIN, header row 14, data rows 15–19, and descending dates. Dates are DD.MM.YYYY text; NAVs are numeric Excel cells. Currency is EUR.", "",
             "Rows 2, 4, 6 contain disclaimers. Rows 9–12 contain Name, ISIN, Currency, As of; As of is 07.10.2026 (export date). Blank spacer rows/columns are ignored. Columns: Date, Asset Under Management, NAV, Index Level, Interim Profits. Only Date/NAV become observations.", "",
             "## File results", "", "| File | Parsed | Clean (includes flagged) | Flagged | Errors | Date range | Missing index | Missing interim profits |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    all_records, all_issues = [], []
    for isin in sorted(INSTRUMENTS):
        for year in (2021, 2023, 2026):
            path = root / "data/raw/phase0" / f"{isin}_{year}_sample.xlsx"
            result = parse_workbook(path, INSTRUMENTS[isin])
            result.clean.to_csv(output / f"{path.stem}_clean.csv", index=False)
            result.records.to_csv(output / f"{path.stem}_all_rows.csv", index=False)
            result.issues.to_csv(output / f"{path.stem}_issues.csv", index=False)
            all_records.append(result.records)
            all_issues.append(result.issues)
            dates = result.clean.observation_date
            bounds = f"{dates.min():%Y-%m-%d}–{dates.max():%Y-%m-%d}" if not dates.empty else "Unavailable"
            flagged = int((result.records.quality_status == "flagged").sum())
            errors = int((result.issues.severity == "error").sum())
            missing = result.structure["optional_missing"]
            lines.append(f"| {path.name} | {len(result.records)} | {len(result.clean)} | {flagged} | {errors} | {bounds} | {missing['Index Level']} | {missing['Interim Profits']} |")
            for row in result.issues.itertuples():
                lines.append(f"\nIssue in {path.name}, worksheet row {row.raw_row_number}: {row.check_code} ({row.severity}). {row.details}")
    combined = pd.concat(all_records, ignore_index=True)
    duplicate_count = int(combined.duplicated(["instrument_code", "observation_date"], keep=False).sum())
    issue_count = sum(len(issues) for issues in all_issues)
    valid_count = int((combined.quality_status == "valid").sum())
    lines += ["", f"Total: {len(combined)} parsed observations; {duplicate_count} rows in cross-file duplicate instrument/date groups.", "",
              "## Findings and assumptions", "", f"Validation produced {issue_count} findings and {valid_count} unflagged valid observations. All outputs are sorted ascending. Missing auxiliary values are counted above; neither auxiliary field is used as NAV.", "",
              "The parser discovers a single Date/NAV table and identity labels, rather than fixing the header position. It accepts native Excel dates or explicit DD.MM.YYYY text and dot-decimal numbers; it does not guess Excel serials or locale-specific numeric separators. Raw row numbers, original values and checksums remain attached. Invalid rows are retained in all_rows output and quarantined from clean output; all duplicate-date members are quarantined. Suspicious positive values remain in clean output as flagged, for manual review.", "",
              "The configurable 20% one-period threshold is a quality heuristic, not a performance output or automatic deletion rule. It runs within each file only. Calendar completeness, missing expected business dates, corporate actions and comparisons across the years-long sample gaps are not assessed.", "",
              "## Readiness", "", f"One parser read all six files: {valid_count} unflagged valid observations. Ready for the observed sample format, not yet certified for full histories. Full-history ingestion needs full-range/calendar checks, corporate-action review, source-use assumptions, larger-file format/precision validation and cross-file conflict handling. This sample-only routine does not load PostgreSQL or compute financial metrics; the completed project analytics and user-reviewed dashboard are documented separately. ML remains absent.", "",
              "## Reproduce", "", "From the repository root: `.venv\\Scripts\\python.exe src/investment_fund_analytics/sample_ingestion.py --root .`. Clean/all-row/issue CSVs are local in data/processed/phase0; this report is tracked. Tests: `.venv\\Scripts\\python.exe -m pytest`. Raw samples are not required for synthetic unit tests; real-sample integration tests skip if local files are absent."]
    report = root / "reports/phase0_sample_quality.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Parsed {len(combined)} observations; report: {report}")


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--root", type=Path, default=Path.cwd())
    run_samples(arguments.parse_args().root.resolve())
