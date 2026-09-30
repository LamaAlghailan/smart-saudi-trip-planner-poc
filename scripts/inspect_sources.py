"""Read-only source inspection using the existing Python environment."""
import csv
import hashlib
import json
import sys
import argparse
import io
from contextlib import redirect_stdout
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def read_workbook(path):
    with ZipFile(path) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rels = {e.attrib['Id']: e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result = {}
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).find('s:sheets', NS):
            rid = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target = rels[rid]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            rows = []
            for row in ET.fromstring(z.read(target)).findall('.//s:sheetData/s:row', NS):
                cells = {}
                for c in row:
                    col = ''.join(x for x in c.attrib['r'] if x.isalpha())
                    index = 0
                    for char in col:
                        index = index * 26 + ord(char) - 64
                    v = c.find('s:v', NS)
                    value = v.text if v is not None else ''
                    if c.attrib.get('t') == 's':
                        value = strings[int(value)]
                    elif c.attrib.get('t') == 'inlineStr':
                        value = ''.join(c.find('s:is', NS).itertext())
                    cells[index - 1] = value
                rows.append([cells.get(i, '') for i in range(max(cells, default=-1) + 1)])
            result[sheet.attrib['name']] = rows
        return result


def main(include_document=False):
    source = ROOT / 'data/raw/items.csv'
    with source.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames
    print('DATA INSPECTION REPORT')
    print('CSV shape:', (len(rows), len(columns)))
    print('All columns:', columns)
    for col in columns:
        counts = Counter(r[col] for r in rows)
        if len(counts) <= 50 or col == 'CityName':
            print(col, 'values:', json.dumps(dict(counts), ensure_ascii=False))
        else:
            print(col, 'unique:', len(counts), 'examples:', list(counts)[:5])
    print('Missing values:', {c: sum(not (r[c] or '').strip() for r in rows) for c in columns})
    print('Duplicate ItemIds:', {k: v for k, v in Counter(r.get('ItemId') for r in rows).items() if v > 1})
    print('Categorical inconsistencies: ItemType has place/Place; category labels mix case and granularity; BudgetLevel has mid/moderate and numeric entries.')
    print('CityName vs CityId distinct counts:', len({r['CityName'] for r in rows}), len({r['CityId'] for r in rows}))
    for col in columns:
        numbers = []
        invalid = []
        for r in rows:
            try:
                numbers.append(float(r[col]))
            except (ValueError, TypeError):
                invalid.append(r[col])
        if numbers:
            print('Numeric profile:', col, 'min', min(numbers), 'max', max(numbers), 'negative', sum(n < 0 for n in numbers), 'zero', numbers.count(0), 'non-numeric count', len(invalid), 'examples', list(dict.fromkeys(invalid))[:5])
    print('Anomaly interpretation: time strings in ages, budget labels in booleans, numeric budgets, text or >5 ratings, and cluster/area text in weather columns indicate shifted data. Do not auto-realign.')
    print('Price maximum 14,500 is a review candidate, not proof of error. Coordinate bounds and date consistency are checked in the derived quality audit.')
    sheets = read_workbook(ROOT / 'data/raw/WVS_Phase2_BirthCountry_Pattern_Results.xlsx')
    print('WVS sheet names:', list(sheets))
    for name, values in sheets.items():
        print('\nSHEET', name, 'rows:', len(values))
        print('HEAD:', json.dumps(values[:4], ensure_ascii=False))
        if values:
            for i, col in enumerate(values[0]):
                if any(x in col.lower() for x in ('country', 'evidence', 'quality', 'eligib', 'rank', 'flag', 'reliab', 'sample')):
                    counts = Counter(r[i] if i < len(r) else '' for r in values[1:])
                    print(col, 'unique:', len(counts), 'values/examples:', dict(list(counts.items())[:12]))
    print('Evidence/quality fields: Raw N, Effective N, Question Coverage (%), Global Baseline (%), Relative vs Global (pp).')
    print('Ranking fields: Eligible for Ranking, Country Rank. 67 eligible and 85 ineligible country groups in supplied workbook.')
    print('STATISTICAL_EFFECTS diagnostics: Eta Squared, Omega Squared, ICC. Phase 1 Semantic Weight and Evidence Tier fields are not supplied in this workbook.')
    if include_document:
        print_document()
    print('\nSOURCE SHA256')
    for path in [source, *ROOT.glob('data/raw/*.xlsx'), *ROOT.glob('docs/*.docx')]:
        print(path.name, hashlib.sha256(path.read_bytes()).hexdigest())


def print_document():
    with ZipFile(ROOT / 'docs/WVS_Tourism_Behavioral_Pattern_Phase1_Phase2.docx') as z:
        root = ET.fromstring(z.read('word/document.xml'))
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        print('\nSOURCE DOCUMENT TEXT')
        for p in root.findall('.//w:p', ns):
            text = ''.join(t.text or '' for t in p.findall('.//w:t', ns))
            if text:
                print(text)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Save a UTF-8 text report as well as printing it.')
    parser.add_argument('--include-document', action='store_true')
    args = parser.parse_args()
    output = io.StringIO()
    with redirect_stdout(output):
        main(args.include_document)
    report = output.getvalue()
    if args.output:
        destination = args.output.resolve()
        allowed = (ROOT / 'outputs').resolve()
        if not destination.is_relative_to(allowed):
            parser.error('--output must be inside the project outputs directory, protecting raw sources')
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(report, encoding='utf-8')
    print(report, end='')
