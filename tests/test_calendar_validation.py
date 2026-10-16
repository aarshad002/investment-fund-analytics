import csv
import json
from pathlib import Path

from investment_fund_analytics.calendar_validation import classify


def test_unknown_gap_is_never_inferred_to_be_a_holiday():
    assert classify('2025-02-04')[0] == 'unresolved'


def test_short_day_does_not_prove_fund_nonvaluation():
    assert classify('2022-12-23')[0] == 'unresolved'
    assert classify('2021-12-24')[0] == 'likely legitimate'


def test_post_change_rule_and_exceptional_uk_holiday_distinguished():
    assert classify('2024-03-29')[0] == 'expected/non-valuation day'
    assert classify('2022-09-19')[0] == 'likely legitimate'


def test_review_register_has_every_gap_once_per_instrument():
    import pytest
    from investment_fund_analytics.calendar_validation import read_register, LOCAL_REGISTER, QUALITY_SUMMARY
    root = Path(__file__).resolve().parents[1]
    if not (root / LOCAL_REGISTER).exists() or not (root / QUALITY_SUMMARY).exists():
        pytest.skip('Authorized local calendar register and quality evidence required')
    rows = read_register(root)
    summary = json.loads((root / QUALITY_SUMMARY).read_text(encoding='utf-8'))
    keys = {(r['isin'], r['gap_date']) for r in rows}
    assert len(keys) == len(rows)
    assert keys == {(isin, day) for isin, details in summary.items() for day in details['missing_weekdays']}


def calendar_fixture(root, omissions=None):
    from investment_fund_analytics.calendar_validation import LOCAL_REGISTER, QUALITY_SUMMARY, COLUMNS
    omissions = ['2025-02-04'] if omissions is None else omissions
    summary = root / QUALITY_SUMMARY; summary.parent.mkdir(parents=True)
    summary.write_text(json.dumps({'TEST': {'missing_weekdays': omissions}}), encoding='utf-8')
    path = root / LOCAL_REGISTER; path.parent.mkdir(parents=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS); writer.writeheader()
        for day in omissions:
            status, reason, evidence = classify(day)
            writer.writerow(dict(isin='TEST',gap_date=day,classification=status,reason=reason,
                                 evidence_codes=evidence,reviewed_on='2026-10-07'))
    return path


def test_local_register_missing_never_uses_public_template(tmp_path):
    import pytest
    from investment_fund_analytics.calendar_validation import read_register
    (tmp_path/'docs').mkdir(); (tmp_path/'docs/calendar_gap_register.csv').write_text('isin,gap_date')
    with pytest.raises(ValueError, match='Local calendar'): read_register(tmp_path)


def test_register_round_trip_and_preserved_reconstruction(tmp_path):
    from investment_fund_analytics.calendar_validation import read_register, build_register
    path=calendar_fixture(tmp_path); before=path.read_bytes()
    assert read_register(tmp_path)[0]['classification']=='unresolved'
    assert build_register(tmp_path)==read_register(tmp_path)
    assert path.read_bytes()==before


def test_register_reconstructs_only_locally(tmp_path):
    from investment_fund_analytics.calendar_validation import build_register
    path=calendar_fixture(tmp_path); path.unlink()  # Disposable test fixture only.
    assert build_register(tmp_path)[0]['isin']=='TEST'
    assert not (tmp_path/'docs/calendar_gap_register.csv').exists()


def test_explicit_zero_gap_summary_accepts_header_only_local_register(tmp_path):
    from investment_fund_analytics.calendar_validation import read_register
    calendar_fixture(tmp_path, [])
    assert read_register(tmp_path)==[]


import pytest
@pytest.mark.parametrize('kind', ['columns','duplicate','date','fund','classification','missing','review_date','reason'])
def test_malformed_or_inconsistent_register_rejected(tmp_path, kind):
    from investment_fund_analytics.calendar_validation import read_register, COLUMNS
    path=calendar_fixture(tmp_path)
    with path.open(encoding='utf-8') as stream: rows=list(csv.DictReader(stream))
    if kind=='duplicate': rows += rows
    elif kind=='missing': rows=[]
    else:
        field={'date':'gap_date','fund':'isin','classification':'classification','review_date':'reviewed_on','reason':'reason'}.get(kind)
        if field:rows[0][field]='invalid'
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=COLUMNS if kind!='columns' else list(reversed(COLUMNS)))
        writer.writeheader();writer.writerows(rows)
    with pytest.raises(ValueError, match='Malformed or inconsistent'):read_register(tmp_path)


def test_reconstruction_refuses_changed_evidence_without_overwriting(tmp_path):
    from investment_fund_analytics.calendar_validation import build_register, QUALITY_SUMMARY
    path=calendar_fixture(tmp_path); original=path.read_bytes()
    (tmp_path/QUALITY_SUMMARY).write_text(json.dumps({'TEST': {'missing_weekdays': []}}),encoding='utf-8')
    with pytest.raises(ValueError,match='inconsistent'):build_register(tmp_path)
    assert path.read_bytes()==original


def test_register_requires_readable_quality_evidence(tmp_path):
    from investment_fund_analytics.calendar_validation import read_register, QUALITY_SUMMARY
    calendar_fixture(tmp_path)
    (tmp_path/QUALITY_SUMMARY).write_text('not json',encoding='utf-8')
    with pytest.raises(ValueError,match='inconsistent'):read_register(tmp_path)
