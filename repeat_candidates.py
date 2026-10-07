"""Flag matching rows from DIFFERENT CSV files. Never deletes transactions.
Teaching example: ISO Date, Description, Amount; optional Balance.
Amounts must be ASCII decimal strings with exactly two decimals.
"""
import argparse
import csv
import json
import sys
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

MONEY = re.compile(r'-?[0-9]+\.[0-9]{2}\Z')

def money(value):
    value = value.strip()
    if not MONEY.fullmatch(value):
        raise ValueError('expected ASCII decimal amount such as -12.00')
    return Decimal(value)

def candidates(paths):
    seen = defaultdict(list)
    output = []
    resolved = [Path(p).resolve() for p in paths]
    if len(set(resolved)) != len(resolved):
        raise ValueError('the same file was supplied twice')
    for path in resolved:
        with path.open(encoding='utf-8-sig', newline='') as source:
            reader = csv.DictReader(source, strict=True)
            if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError(f'{path.name}: missing or duplicate headers')
            required = {'Date', 'Description', 'Amount'}
            if not required.issubset(reader.fieldnames):
                raise ValueError(f'{path.name}: requires Date, Description, Amount')
            for row_number, row in enumerate(reader, start=2):
                if None in row or any(v is None for v in row.values()):
                    raise ValueError(f'{path.name}:{row_number}: wrong column count')
                try:
                    raw_date = row['Date'].strip()
                    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', raw_date):
                        raise ValueError('expected ISO date YYYY-MM-DD')
                    day = date.fromisoformat(raw_date)
                    description = row['Description'].strip()
                    if not description:
                        raise ValueError('blank description')
                    amount = money(row['Amount'])
                    balance = money(row['Balance']) if 'Balance' in row else None
                except ValueError as error:
                    raise ValueError(f'{path.name}:{row_number}: {error}') from error
                key = (day, description, amount)
                current = {'file': str(path), 'record': row_number, 'balance': balance}
                for previous in seen[key]:
                    if previous['file'] == str(path):
                        continue
                    if balance is not None and previous['balance'] is not None and balance != previous['balance']:
                        continue
                    reason = 'matching balance' if balance is not None and previous['balance'] is not None else 'balance unavailable'
                    output.append({'earlier': previous, 'later': current, 'reason': reason})
                seen[key].append(current)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description='Flag cross-file bank-row matches. Never deletes rows. One account and currency only.')
    parser.add_argument('files', nargs='+', type=Path, help='CSV exports with Date, Description, Amount; optional Balance')
    args = parser.parse_args(argv)
    try:
        matches = candidates(args.files)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        print(f'Input rejected: {error}', file=sys.stderr)
        return 2
    # JSON output is deliberately not CSV and contains no merchant descriptions.
    print(json.dumps(matches, default=str, indent=2))
    print(f'{len(matches)} candidate pairs. No rows removed. Review original statements.', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
