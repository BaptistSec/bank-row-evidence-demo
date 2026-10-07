# Two bank rows look the same. Should you delete one?

Keep the original files from your bank. Compare only one account and currency, and mark matching rows for review rather than deleting them. Two real purchases can have the same date, description and amount. Matching balances and knowing which file each row came from narrow the rows to check, but still do not prove they describe the same transaction.

This demonstration runs a small program written in Python on made-up bank files. It only reads the input files; it does not change them. The files use CSV (comma-separated values), a text format for rows and columns. The examples show one pair of rows worth checking with matching balances, two less certain pairs when balances are missing, no pair when one amount is positive and the other negative, and rejection of an amount in the wrong format.

## What this script does, and doesn't do

The teaching script compares rows from different files with matching date, exact description and amount. When both rows have a Balance value, it also requires the balances to match. If either file lacks the Balance column, it labels the pair "balance unavailable".

It never deletes rows or writes a cleaned statement. A candidate pair means two rows worth checking, not two proven copies of one transaction. It prints those pairs in JSON, a structured text format, plus a summary. It is a separate teaching example, not the paid Bank Statement Cleaner's source code.

Use only these input rules:

- CSV with commas between columns, saved as UTF-8, a text-saving format. When saving or exporting the file, choose UTF-8. A UTF-8 byte-order mark (a marker at the start of some text files) is accepted;
- column names Date, Description and Amount, with optional Balance;
- dates in year-month-day order, such as 2026-09-30;
- amounts using ordinary digits 0-9, a decimal point and an optional minus sign, with exactly two decimal places, such as -3.00;
- one account and one currency across every file.

Descriptions must have the same capital and lower-case letters after spaces at their start and end are removed. The program does not work out whether different names mean the same shop, convert currencies, identify accounts or distinguish pending transactions from final entries. Keep real bank files private; the report includes their locations on your computer.

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

The two rows in main.csv could be genuine purchases. Their running balances differ. The overlapping export is made up as a second export of the earlier row, not another purchase. Its balance matches the first purchase. The program cannot establish that story from the row values.

You need Python 3 installed to run this example. Open a terminal, the application where you type commands. Move to the main folder of the downloaded and unzipped demonstration, then run the supplied repeat_candidates.py program:

```sh
python3 repeat_candidates.py examples/main.csv examples/overlap.csv
```

Actual result from the demonstration: one candidate pair, main.csv record 2 and overlap.csv record 2, reason "matching balance". Record numbers count the rows the program reads, including the column-name row. They are not necessarily the same as text line numbers, because a quoted value can span lines.

The summary is:

```text
1 candidate pairs. No rows removed. Review original statements.
```

The second coffee in main.csv is not included in that pair. The script also deliberately skips same-file matches, even if every field is identical. That is a limit, not proof those rows are valid.

Before changing records, check the original bank statement or the bank's transaction reference. Matching balances can coincide, especially if you accidentally mix accounts. This result identifies a place to look, not a transaction safe to remove.

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

This is why the number of pairs to review is not the number of duplicate transactions. One row can appear in several pairs. Don't subtract the pair count from your transaction count or totals.

If a Balance column exists but a cell is blank or in the wrong format, the program rejects the input. It does not treat a bad value as if there had been no balance information.

## 3. Positive and negative amounts are different

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

The positive amount does not match -3.00. The program has not proven these entries are a purchase and its refund or reversal. It keeps positive and negative amounts separate. Check the bank records, not the made-up example's filename, to find out whether they are related.

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

Actual result: the program returns status code 2, meaning it rejected the input. It produces no JSON result and prints this error:

```text
Input rejected: invalid.csv:2: expected ASCII decimal amount such as -12.00
```

That error asks for digits 0-9, a decimal point, exactly two decimal places and an optional minus sign.

Rounding -3.001 to -3.00 would make a data change the reader might not notice. This program accepts only the stated format, so it rejects that amount. It also rejects NaN and Infinity (special number values that are not valid amounts here), dates not in the stated format, repeated column names and rows with the wrong number of columns.

Extra zeros at the start of an amount do not change its value, and -0.00 is treated as equal to 0.00. For developers: the program uses Python Decimal for decimal arithmetic.[1] It reads rows with csv.DictReader and opens files with newline='', following the Python CSV documentation.[2] You do not need to change these settings to run the example.

## 5. Verify that the exercise didn't change the inputs

On the Linux demonstration computer, we recorded file fingerprints (SHA-256 hashes), numbers calculated from each file's contents, before and after the four runs. A fingerprint helps check whether a file's contents changed. These commands require the sha256sum and diff programs:

```sh
sha256sum examples/*.csv > before.sha256
# Run the demonstration commands above.
sha256sum examples/*.csv > after.sha256
diff before.sha256 after.sha256
```

The sha256sum commands calculate SHA-256 file fingerprints. The diff command compares the two lists. The comparison found no differences. The supplied records include both fingerprint lists and the program's results. This checks that the input files did not change in this exercise. It does not promise that another program will leave them unchanged.

The program displays results and errors in the terminal. Results go to standard output (stdout), and summaries and errors go to standard error (stderr), two separate output channels. If you use a command to save that text to a file, choose a new report filename, never an input filename. The terminal can overwrite the destination before the program reads its input.

## What was tested

On 7 October 2026, the four demonstrated runs and the existing 27 automated checks using made-up data passed on Linux with Python 3.10.12. The checks cover displayed results and errors, unchanged input files, wrongly formatted CSV, dates, amounts, commas inside quoted values, text-file markers, matching rules and row numbering.

Windows, macOS, real bank files and speed on large files were not tested. Many banks use other columns, date formats or ways of showing money paid out and received. Do not force a real bank file into this format by guessing plus or minus signs or rounding amounts.

Keep originals, review candidates against source records and check row counts and totals agree before and after any separate approved removal process. This small-file teaching script can produce many pairs when matching rows repeat. It cannot decide which transaction to remove.

## Optional next step

You can run the demonstration without buying anything. The optional [Bank Statement Cleaner](https://payhip.com/b/SruFD?utm_source=substack&utm_medium=article&utm_campaign=csv_repeat_evidence) from Tidy Desk Digital has a broader process for cleaning files and setting aside rows it cannot read and optional removal of repeated rows. Its code and tests are separate from this example; read its current description of what it does and which computers were tested before using it.

## Sources and demonstration files

[1] Python Decimal:
https://docs.python.org/3/library/decimal.html

[2] Python CSV:
https://docs.python.org/3/library/csv.html

The accompanying demonstration bundle contains the original teaching script, 27 automated checks, made-up input files, actual results, errors and before/after file fingerprints. Source and listing checked 7 October 2026. This walkthrough is included with the demonstration files.
