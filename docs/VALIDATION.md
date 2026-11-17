# Validation performed

- Ran the full pipeline against the original UCI Online Retail workbook: 541,909 rows.
- The successful rerun rebuilt the CSV reports and SQLite database; 10 reconciliation/invariant checks passed (see reports/run_metadata.json).
- Two standard-library unittest cases passed: classification of sales, credits, duplicates, missing IDs and malformed rows; and SQL treatment of credit-only products, partial-window exclusion and observed zero-retention months.
- Streamlit AppTest rendered all three tabs without exceptions and exercised the monthly-measure selector, UK exclusion checkbox and product-sales threshold.
- Tested on Python 3.12 in Linux. Package versions are recorded in tested-environment.txt. Your Mac/Python 3.13 installation still needs a local run; operating-system compatibility has not been tested on your device.
- Dashboard checks were programmatic; a human visual review on your Mac is still needed before publishing screenshots.
