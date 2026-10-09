#!/usr/bin/env python3
"""Check the released inputs and numbering without R or confidential data."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import re
import sys

CODE = Path(__file__).resolve().parent
DEFAULT_DATA = CODE.parent / 'data' / 'non-confidential'
EXPECTED_PANELS = {12: set('AB'), 13: set('ABCD'), 27: set('AB'), 28: set('AB'),
                   29: set('ABCDE'), 31: set('ABC'), 32: set('ABCDEFGHI'),
                   33: set('ABCDE'), 34: set('ABC')}
EXPECTED_FIGURES = {16: 'Supp_Fig_16.py', 17: 'Supp_Fig_17.R',
                    18: 'Supp_Fig_18.R', 19: 'Supp_Fig_19.py'}
CHANNELS = ('Own funds', 'Bank loan or installer finance', 'Loan from relatives or friends',
            'Financial assistance from relatives or friends', 'Financial contribution from children',
            'Government or collective subsidy', 'Other funding source')

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    require(bool(fields) and bool(rows), f'Empty CSV: {path.name}')
    require(len(fields) == len(set(fields)), f'Duplicate CSV headers: {path.name}')
    require(all(None not in row and all(value is not None for value in row.values()) for row in rows),
            f'Ragged CSV rows: {path.name}')
    return fields, rows

def check_financing(data_dir: Path) -> dict:
    _, rows = read_csv(data_dir / 'supp_table17.csv')
    panel = [row for row in rows if row['panel_label'].startswith('Panel F')]
    require(len(panel) == 7, 'Table 17 Panel F must contain seven funding channels.')
    require({r['Funding channel'] for r in panel} == set(CHANNELS), 'Table 17 Panel F channels do not match.')
    _, counts = read_csv(data_dir / 'financing_current_income_counts.csv')
    require(len(counts) == 14, 'Expected fourteen aggregate financing count rows.')
    lookup = {(r['income_group'], r['funding_channel']): r for r in counts}
    require(len(lookup) == 14, 'Duplicated financing count keys.')
    for row in panel:
        for group, expected_n in [('Lower', 492), ('Higher', 497)]:
            key = (group, row['Funding channel'])
            require(key in lookup, f'Missing aggregate count: {key}')
            count_row = lookup[key]
            n = float(count_row['households']); users = float(count_row['users'])
            require(n == expected_n and n.is_integer(), f'{group} financing denominator must be {expected_n}.')
            require(users.is_integer() and 0 <= users <= n, f'Invalid user count: {key}')
            expected = 100 * users / n
            require(float(row[f'{group} current income N']) == expected_n,
                    f'Table 17 Panel F {group} N must be {expected_n}; do not use 496 or 517/516.')
            for observed in [count_row['use_percent'], row[f'{group} current income use prevalence (%)']]:
                require(math.isclose(float(observed), expected, rel_tol=0, abs_tol=1e-9),
                        f'Percentage does not equal 100 * users / N: {key}')
    # Unconditional financing summaries use all adopters, not the income-complete subsample.
    overall = {r['Funding channel']: r for r in rows if r['panel_label'].startswith('Panel A')}
    require(len(overall) == 7, 'Table 17 Panel A is incomplete.')
    for row in overall.values():
        require(float(row['All adopters']) == 1033, 'Do not restrict the overall financing denominator to 989.')
    require(float(overall['Bank loan or installer finance']['Adopters using channel']) == 185,
            'The overall bank/installer count must remain 185.')
    require(float(overall['Financial contribution from children']['Adopters using channel']) == 339,
            'The overall child-contribution count must remain 339.')
    _, appliances = read_csv(data_dir / 'supp_table29.csv')
    for row in appliances:
        if row['panel'] in {'A', 'C', 'D', 'E'}:
            # Some questions have item-specific denominators; they cannot exceed the income groups.
            require(float(row['group_1_n']) <= 492 and float(row['group_2_n']) <= 497,
                    'Table 29 has a current-income denominator larger than 492/497.')
    return {'current_income_households': 989, 'lower_income': 492, 'higher_income': 497,
            'median_annual_pc_income_rmb': 15960, 'lower_rule': '<', 'higher_rule': '>=',
            'financing_channels': 7, 'unconditional_adopters': 1033}

def check_figure3(main_dir: Path) -> None:
    _, rows = read_csv(main_dir / 'figure3_plot_data.csv')
    for panel, n in [('a', 9), ('b', 5), ('c', 23), ('d', 23)]:
        selected = [r for r in rows if r['panel'] == panel]
        require(len(selected) == n, f'Figure 3 panel {panel}: expected {n} rows.')
        require(sorted(int(r['x_order']) for r in selected) == list(range(1,n+1)),
                f'Figure 3 panel {panel}: duplicate or missing positions.')
    b = sorted((r for r in rows if r['panel'] == 'b'), key=lambda r: int(r['x_order']))
    labels = ['Past outages / unstable voltage', 'Future outages / rationing in heat',
              'Grid-tied PV: no outage backup', 'Maintain basic services in outages',
              'Maintain AC in outages']
    require([r['x_label'] for r in b] == labels, 'Figure 3b motive labels/order are not current.')
    require([int(float(r['count'])) for r in b] == [32,47,56,77,10],
            'Figure 3b motive counts are not aligned with labels.')
    for r in b:
        require(float(r['denominator']) == 194, 'Figure 3b denominator must be 194.')
        require(math.isclose(float(r['share_percent']),100*float(r['count'])/194,abs_tol=1e-9),
                'Figure 3b shares must agree with counts.')

def validate(data_dir: Path = DEFAULT_DATA, code_dir: Path = CODE) -> dict:
    data_dir = data_dir.resolve(); code_dir = code_dir.resolve()
    supplementary = data_dir / 'aggregate_supplementary'
    main = data_dir / 'aggregate_main'
    require(main.is_dir() and supplementary.is_dir(), 'Expected aggregate_main/ and aggregate_supplementary/.')
    notes = json.loads((supplementary / 'supplementary_table_notes.json').read_text(encoding='utf-8'))
    require(set(notes) == {str(n) for n in range(1,36)}, 'Table notes must cover Tables 1–35 exactly.')
    _, index = read_csv(code_dir / 'supplementary_table_index.csv')
    require(sorted(int(r['table']) for r in index) == list(range(1,36)), 'Table index is incomplete or duplicated.')
    expected_sources = set()
    for item in index:
        n = int(item['table'])
        require(item['title'] == notes[str(n)]['title'], f'Table {n} title/index mismatch.')
        require(item['title'].startswith(f'Supplementary Table {n}:'), f'Table {n} carries an old title number.')
        for filename in item['source_files'].split(';'):
            require(re.fullmatch(rf'supp_table{n:02d}(?:_panel[A-Z])?\.csv',filename) is not None,
                    f'Unexpected source name for Table {n}: {filename}')
            expected_sources.add(filename)
            _, rows = read_csv(supplementary / filename)
            if 'table_number' in rows[0]:
                require(all(int(r['table_number']) == n for r in rows), f'Old table_number field in {filename}.')
            if n in EXPECTED_PANELS:
                require({r['panel'] for r in rows} == EXPECTED_PANELS[n], f'Table {n} panel structure mismatch.')
    require(expected_sources == {p.name for p in supplementary.glob('supp_table*.csv')},
            'Unexpected or obsolete Supplementary Table CSV files; use the complete release package.')
    for n in [13,17,29]:
        require('989' in notes[str(n)]['notes'] and '15,960' in notes[str(n)]['notes'],
                f'Table {n} notes must describe the harmonized current-income definition.')
    financing = check_financing(supplementary)
    _, matched = read_csv(supplementary / 'supp_table28.csv')
    smd = {r['row_id']: float(r['estimate']) for r in matched
           if r['panel'] == 'A' and r['column_id'] == 'matched_smd'}
    require(sorted(round(v,3) for v in smd.values()) == [-0.037,-0.036,0.044,0.047],
            'Table 28 must retain the four signed after-matching SMD values.')
    _, balance = read_csv(supplementary / 'supp_table21.csv')
    require(len(balance) == 4 and 'treatment_mean' in balance[0], 'Table 21 must contain all four balance rows.')
    for section, manifest_name, total in [('main','main_figure_manifest.csv',6),
                                          ('supplementary','supplementary_figure_manifest.csv',27)]:
        _, entries = read_csv(code_dir / manifest_name)
        ids=[]
        for entry in entries:
            require((code_dir / section / entry['script']).is_file(), f'Missing script: {entry["script"]}')
            figure=entry['figure']
            ids.extend(range(int(figure.split('-')[0]), int(figure.split('-')[-1])+1))
        require(sorted(ids) == list(range(1,total+1)), f'{section}: duplicate or missing figure numbers.')
        by_id={r['figure']:r['script'] for r in entries}
        if section=='supplementary':
            for n,s in EXPECTED_FIGURES.items():require(by_id.get(str(n))==s,f'Old Supplementary Figure {n} mapping.')
        else:require(by_id.get('3')=='Figure_3.py','The approved Figure 3 Python script is not selected.')
    for section, manifest_name, total in [('main', 'main_figure_manifest.csv', 6),
                                          ('supplementary', 'supplementary_figure_manifest.csv', 27)]:
        _, entries = read_csv(code_dir / manifest_name)
        require(len(entries) == total, f'{section}: one complete script is required per figure.')
        for entry in entries:
            number = int(entry['figure'])
            suffix = '.R' if entry['interpreter'] == 'Rscript' else '.py'
            expected_name = (f'Figure_{number}' if section == 'main' else f'Supp_Fig_{number:02d}') + suffix
            require(entry['script'] == expected_name, f'Unexpected figure filename: {entry["script"]}')
        expected = {entry['script'] for entry in entries}
        if section == 'supplementary':
            expected.add('Supplementary_Tables.py')
        directory = code_dir / section
        actual = {p.name for p in directory.iterdir() if p.name != '__pycache__'}
        require(actual == expected,
                f'{section}: expected only the named figure scripts; remove old helpers/folders after backup. '
                f'Extra: {sorted(actual - expected)}; missing: {sorted(expected - actual)}')
        require(all((directory / name).is_file() for name in expected),
                f'{section}: a directory occupies a script path.')
    check_figure3(main)
    obsolete_data=['supp_fig16_comparability_density.csv','supp_fig16_overlap_audit.csv',
                   'supp_fig18_hourly_profile_2020.csv','supp_fig18_survey_frequencies.csv',
                   'supp_fig19_propensity_density.csv']
    stale = [str(supplementary/p) for p in obsolete_data if (supplementary/p).exists()]
    require(not stale,'Remove obsolete release files after backing them up: '+', '.join(stale))
    return {'status':'success','release':'2026-10-09','layout_revision':'2026-10-09-clean-names','main_figures':6,'supplementary_figures':27,
            'supplementary_tables':35,'table_csv_files':len(expected_sources),'financing':financing,
            'figure3_motive_order':'verified','table28_postmatching_smd':'verified',
            'confidential_records_required':False}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=DEFAULT_DATA)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    try:
        result=validate(args.data_dir)
        if args.report:
            args.report.parent.mkdir(parents=True,exist_ok=True)
            args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print('Public input validation: SUCCESS')
        print('Tables 1-35; figures 1-6 and 1-27; current-income groups 492/497; Figure 3b order and clean script layout checked.')
        return 0
    except (ValueError,FileNotFoundError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(f'PUBLIC INPUT VALIDATION FAILED: {exc}',file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())
