"""Annotate observed calendar gaps from reviewed evidence; never invent NAV dates."""
from collections import Counter
import csv
import json
from pathlib import Path

REASONS = {
    '2021-11-01': ('Luxembourg All Saints', 'LU'),
    '2021-12-24': ('Christmas Eve banking half-day; issuer banking-day rule excludes half-days', 'LU,OLD'),
    '2021-12-27': ('UK Christmas substitute', 'UK'),
    '2021-12-28': ('UK Boxing Day substitute', 'UK'),
    '2022-01-03': ('UK New Year substitute', 'UK'),
    '2022-04-15': ('Good Friday', 'TARGET,UK'),
    '2022-04-18': ('Easter Monday', 'TARGET,UK,LU'),
    '2022-05-02': ('UK early May bank holiday', 'UK'),
    '2022-05-09': ('Luxembourg Europe Day', 'LU'),
    '2022-05-26': ('Luxembourg Ascension', 'LU'),
    '2022-06-02': ('UK shifted spring bank holiday', 'UK'),
    '2022-06-03': ('UK Platinum Jubilee bank holiday', 'UK'),
    '2022-06-06': ('Luxembourg Whit Monday', 'LU'),
    '2022-06-23': ('Luxembourg National Day', 'LU'),
    '2022-08-15': ('Luxembourg Assumption', 'LU'),
    '2022-08-29': ('UK summer bank holiday', 'UK'),
    '2022-09-19': ('UK Queen Elizabeth II funeral bank holiday', 'UK'),
    '2022-11-01': ('Luxembourg All Saints', 'LU'),
    '2022-12-23': ('Some venues had Christmas Eve substitute half-day; no fund-specific exclusion verified', 'EXCHANGE'),
    '2022-12-26': ('Boxing Day', 'TARGET,UK,LU'),
    '2022-12-27': ('UK Christmas substitute', 'UK'),
    '2023-01-02': ('UK New Year substitute', 'UK'),
    '2023-04-07': ('Good Friday', 'TARGET,UK'),
    '2023-04-10': ('Easter Monday', 'TARGET,UK,LU'),
    '2023-05-01': ('Labour Day / UK early May', 'TARGET,UK,LU'),
    '2023-05-08': ('UK coronation bank holiday', 'UK'),
    '2023-05-09': ('Luxembourg Europe Day', 'LU'),
    '2023-05-18': ('Luxembourg Ascension', 'LU'),
    '2023-05-29': ('Luxembourg Whit Monday / UK spring bank holiday', 'LU,UK'),
}


def classify(day):
    if day in REASONS:
        reason, evidence = REASONS[day]
        status = 'unresolved' if day == '2022-12-23' else 'likely legitimate'
        return status, reason, evidence
    # Enumerate reviewed dates, not every hypothetical missing date.
    known = {
        '2023-12-25': 'Christmas', '2023-12-26': 'Boxing Day',
        '2024-01-01': 'New Year', '2024-03-29': 'Good Friday', '2024-04-01': 'Easter Monday',
        '2024-12-25': 'Christmas', '2024-12-26': 'Boxing Day',
        '2025-01-01': 'New Year', '2025-04-18': 'Good Friday', '2025-04-21': 'Easter Monday',
        '2025-12-25': 'Christmas', '2025-12-26': 'Boxing Day',
        '2026-01-01': 'New Year', '2026-04-03': 'Good Friday', '2026-04-06': 'Easter Monday',
    }
    if day in known:
        return 'expected/non-valuation day', known[day] + '; matches explicit issuer NAV-date exclusions', 'NEW,TARGET'
    return 'unresolved', 'No reviewed date-specific evidence', ''


COLUMNS = ('isin', 'gap_date', 'classification', 'reason', 'evidence_codes', 'reviewed_on')
LOCAL_REGISTER = Path('data/interim/calendar/calendar_gap_register.csv')
QUALITY_SUMMARY = Path('data/processed/full_history/quality_summary.json')


def read_register(root):
    """Require reviewed local records matching independently observed omissions."""
    from datetime import date
    path = root / LOCAL_REGISTER
    summary_path = root / QUALITY_SUMMARY
    if not path.is_file() or not summary_path.is_file():
        raise ValueError('Local calendar register and quality summary required; reconstruct and review before loading')
    try:
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        expected = {(isin, day) for isin, details in summary.items() for day in details['missing_weekdays']}
        if not summary or not all(isinstance(details['missing_weekdays'], list) for details in summary.values()):
            raise ValueError('Invalid quality summary')
        for isin, details in summary.items():
            days = details['missing_weekdays']
            if not isinstance(isin, str) or len(days) != len(set(days)):
                raise ValueError('Invalid or duplicate quality evidence')
        for isin, day in expected:
            if date.fromisoformat(day).isoformat() != day:
                raise ValueError('Noncanonical quality date')
        with path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            if tuple(reader.fieldnames or ()) != COLUMNS:
                raise ValueError('Invalid calendar columns')
            rows = list(reader)
        keys = set()
        for row in rows:
            if set(row) != set(COLUMNS) or any(value is None for value in row.values()):
                raise ValueError('Malformed calendar row')
            key = (row['isin'], row['gap_date'])
            date.fromisoformat(row['gap_date']); date.fromisoformat(row['reviewed_on'])
            if key in keys or key not in expected:
                raise ValueError('Duplicate or unexpected fund/date')
            keys.add(key)
            status, reason, evidence = classify(row['gap_date'])
            if (row['classification'], row['reason'], row['evidence_codes']) != (status, reason, evidence):
                raise ValueError('Calendar decision differs from reviewed classification rules')
        if keys != expected:
            raise ValueError('Calendar register does not cover observed omissions')
        return rows
    except (KeyError, TypeError, AttributeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError('Malformed or inconsistent local calendar evidence; review required') from exc


def build_register(root):
    """Reconstruct locally; never overwrite a preserved reviewed register."""
    import io
    summary = json.loads((root / QUALITY_SUMMARY).read_text(encoding='utf-8'))
    rows = []
    for isin, details in sorted(summary.items()):
        for day in details['missing_weekdays']:
            status, reason, evidence = classify(day)
            rows.append(dict(isin=isin, gap_date=day, classification=status, reason=reason,
                             evidence_codes=evidence, reviewed_on='2026-10-07'))
    output = root / LOCAL_REGISTER
    if output.exists():
        existing = read_register(root)
        if existing != rows:
            raise ValueError('Existing local register preserved; reconcile revised inputs separately')
        return existing
    output.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS)
    writer.writeheader(); writer.writerows(rows)
    with output.open('xb') as stream:
        stream.write(buffer.getvalue().encode('utf-8'))
    return read_register(root)


if __name__ == '__main__':
    build_register(Path.cwd())
