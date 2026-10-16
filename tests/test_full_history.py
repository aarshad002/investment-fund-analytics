from decimal import Decimal

import pandas as pd

from investment_fund_analytics.full_history import consolidate, weekday_gaps


def frame(values, filename='full.xlsx'):
    return pd.DataFrame([dict(instrument_code='ISIN:NAV:EUR:NATIVE',
                              observation_date=pd.Timestamp(day), value=Decimal(value),
                              raw_file=filename, quality_status=status)
                         for day, value, status in values])


def test_identical_overlap_has_explicit_lineage_and_no_duplicates():
    full = frame([('2023-10-02', '100', 'valid'), ('2023-10-03', '101', 'valid')])
    sample = frame([('2023-10-02', '100.0', 'valid')], 'sample.xlsx')
    clean, conflicts, summary = consolidate([full, sample])
    assert len(clean) == 2 and conflicts.empty
    assert summary['overlap_dates'] == summary['identical_extra_rows'] == 1
    assert clean.iloc[0].raw_file == 'full.xlsx'
    assert 'sample.xlsx' in clean.iloc[0].supporting_files


def test_conflicting_overlap_preserves_both_versions_and_excludes_date():
    clean, conflicts, summary = consolidate([
        frame([('2023-10-02', '100', 'valid')]),
        frame([('2023-10-02', '100.01', 'valid')], 'sample.xlsx')])
    assert clean.empty and len(conflicts) == 2
    assert set(conflicts.value) == {Decimal('100'), Decimal('100.01')}
    assert summary['conflict_dates'] == 1


def test_flags_survive_overlap_and_invalid_rows_are_counted():
    clean, _, summary = consolidate([
        frame([('2023-10-02', '100', 'valid'), ('2023-10-03', '0', 'invalid')]),
        frame([('2023-10-02', '100', 'flagged')], 'sample.xlsx')])
    assert len(clean) == 1 and clean.iloc[0].quality_status == 'flagged'
    assert summary['invalid_rows'] == 1


def test_weekday_gap_screen_does_not_invent_weekend_observations():
    rows = frame([('2023-10-06', '100', 'valid'), ('2023-10-10', '101', 'valid')])
    assert weekday_gaps(rows, '2023-10-06', '2023-10-10') == ['2023-10-09']
