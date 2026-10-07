# Read-only bank-row demonstration
Synthetic teaching inputs, not real bank records. Tested 7 Oct 2026, Linux Python 3.10.12.
Run python3 -m unittest -v for 27 tests. Run repeat_candidates.py on matching input CSVs to print JSON candidate pairs, never remove rows. Preserve originals. Compare one account/currency only; narrow ISO dates and ASCII two-decimal amounts. See WALKTHROUGH.md for the complete walkthrough and limits.
Actual outputs are captured in matching.json, missing-balance.json, reversal.json and summaries; malformed input error/status captured too. before.sha256 and after.sha256 show original synthetic input bytes unchanged. Local absolute paths in outputs are this demonstration's temporary paths; your paths differ.
Public package excludes internal research/context files. No claim of Windows/macOS or bank-by-bank tests. The teaching code is separate from the commercial product.

Published by William Baptist | Tidy Desk Digital
