# Study after the first working run

1. **Business problem:** Explain who would use this analysis and which decisions it can support.
2. **One row versus one order:** Demonstrate why summing rows counts invoice lines, while COUNT(DISTINCT invoice_no) counts orders.
3. **Python preparation:** Follow prepare() in retail_pipeline.py. Explain strings, missing values, boolean masks, row statuses and why negative quantities are not automatically errors.
4. **Exclusion decisions:** Compare missing customer IDs with missing invoice dates. Explain why the former can remain in sales analysis.
5. **SQL:** Read files in order: shared views; aggregates/CROSS JOIN; monthly CTEs/LAG; product LEFT JOIN; country GROUP BY; customer NTILE; cohort grid and denominators.
6. **Metrics:** Recalculate one invoice by hand. Distinguish gross sales, credits, net merchandise value and profit (unavailable).
7. **Retention:** Explain month 0, follow-up time, first observed versus acquired, and blank versus zero heatmap cells.
8. **Validation:** Explain what each run_metadata.json check verifies. Read the small synthetic classification regression test.
9. **Dashboard:** Trace every visual to a reports CSV and that CSV to its SQL query. Explain which controls affect which visual.
10. **Reproducibility:** Explain .gitignore, requirements, source hash, relative file paths and how another person can reproduce the work.

## Interview prompts

- Why didn't you delete every missing customer ID?
- Why are negative non-C lines quarantined?
- Is your credit ratio the true return rate?
- What happens if duplicate-looking lines are legitimate?
- Why omit December 2011 from comparisons?
- Do your segments establish that a customer has churned?
- How would you test whether a retention campaign actually works?
- Which work was AI-assisted, and what did you verify yourself?

## Improvements you can make yourself

Prioritise a duplicate-treatment sensitivity analysis and better nonstandard product-code investigation. Later consider cohort follow-up comparisons at a common horizon, and tests using another dataset. Avoid adding machine learning before understanding the descriptive analysis.
