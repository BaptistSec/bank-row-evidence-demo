# Check similar bank rows without deleting them

This free example uses made-up bank records. It marks matching rows in different spreadsheet export files for you to review. A match is not proof that either row is a duplicate. The program does not remove rows or change the input files.

You need Python installed to run it. Open a command window in the folder containing `repeat_candidates.py`, then run:

Swipe code sideways if a line is cut off.

```sh
python3 repeat_candidates.py \
examples/main.csv \
examples/overlap.csv
python3 -m unittest -v
```

The first command checks two supplied example files. The second runs the 27 automated checks supplied with the program. Those checks passed on Linux with Python 3.10.12 on 7 October 2026. Windows, macOS and exports from real banks have not been tested.

## Keep the limits in mind

- Keep your original bank exports. Check any matching rows against the bank's own records before changing anything.
- Compare files from one account, using one currency. The program cannot check that you have done this.
- This example accepts comma-separated text files, called CSV files. Dates must use year-month-day, such as `2026-09-30`. Amounts must use digits 0-9, a decimal point and exactly two decimal places, such as `-3.00`.
- The program prints a structured text report, called JSON, listing pairs of rows to review. It does not produce a cleaned statement. The report includes file locations on your computer; keep real reports private.
- If you save the report to a file, choose a new filename. Never save it over an input file.

Read `WALKTHROUGH.md` for the step-by-step examples and full limits. The supplied report files and summaries show the actual example runs. `before.sha256` and `after.sha256` contain matching file fingerprints, which show that the made-up input files were unchanged during those runs. File locations in the saved reports belong to the demonstration computer; yours will differ.

This teaching example is separate from the paid Bank Statement Cleaner. You do not need to buy anything to run it.

Published by William Baptist | Tidy Desk Digital
