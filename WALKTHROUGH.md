# Two identical bank CSV rows: test the evidence before deleting either

Keep the original exports, compare only one account and currency, and flag matching rows for review rather than deleting them. A matching date, description and amount can be two real purchases. Matching balances and source-file provenance narrow the candidates, but still don't prove transaction identity.

The demonstration below runs a read-only Python script on fictional CSVs. It shows one matching-balance pair, two weaker pairs when balance evidence is missing, no pair for an opposite-sign reversal, and rejection of a malformed amount. The input bytes remain unchanged.

## What this script does, and doesn't do

The teaching script compares rows from different files with matching date, exact description and amount. When both rows have a Balance value, it also requires the balances to match. If either file lacks the Balance column, it labels the pair "balance unavailable".

It never deletes rows or writes a cleaned statement. It prints JSON candidate pairs and a summary. It is a separate teaching example, not the paid Bank Statement Cleaner's source code.

Use only these input rules:

- comma-delimited UTF-8 CSV, with optional UTF-8 BOM;
- Date, Description and Amount headers, with optional Balance;
- ISO dates such as 2026-09-30;
- ASCII amounts with exactly two decimal places, such as -3.00;
- one account and one currency across every file.

Descriptions are case-sensitive after trimming outer spaces. The script doesn't interpret merchant aliases, exchange rates, account identity or pending-versus-posted transactions. Keep real exports private; the report includes local paths.

## 1. Two coffees, one overlap

These transactions and balances are invented. The extracted bundle already contains this fictional examples/main.csv:

```csv
Date,Description,Amount,Balance
2026-09-30,Coffee,-3.00,97.00
2026-09-30,Coffee,-3.00,94.00
```

It also contains examples/overlap.csv:

```csv
Date,Description,Amount,Balance
2026-09-30,Coffee,-3.00,97.00
```

The two rows in main.csv could be genuine purchases. Their running balances differ. The overlapping export contains a row matching the first purchase, including its balance.

Run the supplied repeat_candidates.py from the extracted bundle root:

```sh
python3 repeat_candidates.py examples/main.csv examples/overlap.csv
```

Actual result from the demonstration: one candidate pair, main.csv record 2 and overlap.csv record 2, reason "matching balance". Record numbers count parsed CSV records, including the header, not physical text lines.

The summary is:

```text
1 candidate pairs. No rows removed. Review original statements.
```

The second coffee in main.csv is not included in that pair. The script also deliberately skips same-file matches, even if every field is identical. That is a limit, not proof those rows are valid.

Before changing records, check the original bank statement or reliable transaction identifier. Matching balances can coincide, especially if you accidentally mix accounts. This result identifies a place to look, not a transaction safe to remove.

## 2. Remove the balance evidence

The bundle contains examples/no_balance.csv:

```csv
Date,Description,Amount
2026-09-30,Coffee,-3.00
```

Run:

```sh
python3 repeat_candidates.py examples/main.csv examples/no_balance.csv
```

Actual result: two pairs, both labelled "balance unavailable". The no-balance row matches both coffees by date, description and amount. The script cannot distinguish them from those fields alone.

```text
2 candidate pairs. No rows removed. Review original statements.
```

This is why a candidate count is not a duplicate count. One row can appear in several pairs. Don't subtract the pair count from your transaction count or totals.

If a Balance column exists but a cell is blank or malformed, the script rejects the input. It doesn't quietly downgrade bad values to absent evidence.

## 3. An opposite-sign row is not the same amount

The bundle contains examples/reversal.csv:

```csv
Date,Description,Amount,Balance
2026-09-30,Coffee,3.00,100.00
```

Run:

```sh
python3 repeat_candidates.py examples/main.csv examples/reversal.csv
```

Actual result:

```text
0 candidate pairs. No rows removed. Review original statements.
```

The positive amount does not match -3.00. The script has not proven a refund or reversal relationship: it merely compares signed amounts. Establish that relationship from the bank records, not from the illustrative filename.

## 4. Reject an amount instead of silently rounding it

The bundle contains examples/invalid.csv:

```csv
Date,Description,Amount,Balance
2026-09-30,Coffee,-3.001,97.00
```

Run:

```sh
python3 repeat_candidates.py examples/invalid.csv
```

Actual result: exit status 2, no JSON result, with this error:

```text
Input rejected: invalid.csv:2: expected ASCII decimal amount such as -12.00
```

Rounding -3.001 to -3.00 would make a data change the reader might not notice. This deliberately narrow parser rejects it. It also rejects NaN, Infinity, ambiguous dates, duplicate headers and wrong column counts.

Leading zeros and negative zero are accepted as numeric equivalents. Amounts use Python Decimal rather than binary floating-point.[1] CSV parsing uses DictReader and newline='', as the Python CSV documentation recommends for file handling.[2]

## 5. Verify that the exercise didn't change the inputs

On the Linux demonstration system, hashes were taken before and after the four runs:

```sh
sha256sum examples/*.csv > before.sha256
# Run the demonstration commands above.
sha256sum examples/*.csv > after.sha256
diff before.sha256 after.sha256
```

The actual comparison returned no differences. The supplied record includes both hash lists and outputs. That verifies unchanged bytes in this exercise; it doesn't mean any other program you run will preserve them.

The script itself prints to stdout/stderr. If you redirect output, use a new report filename, never an input filename. Shell redirection can overwrite a file before the script reads it.

## What was tested

On 7 October 2026, the four demonstrated runs and the existing 27 synthetic unit tests passed on Linux with Python 3.10.12. The tests cover CLI output/error handling, unchanged inputs, malformed CSV, dates, decimal validation, quoted commas, BOMs, matching rules and parsed-record numbering.

Windows, macOS, real-bank export compatibility and performance on large files were not tested. Many banks use other columns, dates or debit/credit conventions. Don't force a real export into this format by guessing signs or rounding values.

Keep originals, review candidates against source records and reconcile counts/totals before and after any separate approved removal process. This small-file teaching script can produce many pairs when matching rows repeat. It is not an accounting decision engine.

## Optional next step

You can run the demonstration without buying anything. The optional [Bank Statement Cleaner](https://payhip.com/b/SruFD?utm_source=substack&utm_medium=article&utm_campaign=csv_repeat_evidence) from Tidy Desk Digital has a broader listed cleanup/rejection workflow and optional repeat removal. Its code and tests are separate from this example; read its current scope and platform limits before using it.

## Sources and demonstration files

[1] Python Decimal:
https://docs.python.org/3/library/decimal.html

[2] Python CSV:
https://docs.python.org/3/library/csv.html

The accompanying demonstration bundle contains the original teaching script, 27-test suite, fictional inputs, actual outputs, errors and before/after hashes. Source and listing checked 7 October 2026. This walkthrough is included with the demonstration files.
