# Methodology and metric definitions

## Row classification (in precedence order)

1. **duplicate:** exact repeat of all eight original columns; retain first. This can remove legitimate repeated invoice lines, so duplicate treatment is an assumption to disclose.
2. **invalid:** missing invoice, product code, date, quantity or price; invalid/non-finite numeric values; fractional item quantities. Missing description, country or customer ID alone does not disqualify a sale.
3. **non_product:** code does not match five digits followed by zero or more letters. This heuristic includes codes like 85123A and excludes POST, DOT, M and discount/service codes. Unusual genuine products may be excluded.
4. **nonpositive_price:** product line with price <= 0.
5. **sale:** eligible product, positive price, positive quantity and invoice not beginning C.
6. **credit:** eligible product, positive price, negative quantity and invoice beginning C.
7. **review:** other combinations, including non-C negative quantities and C positive quantities. Preserve, do not silently convert.

Classification is mutually exclusive and covers every raw row. Text is trimmed, invoices/codes uppercased, IDs stored as strings, blank text treated as missing. Monetary line values are quantity × unit price, rounded to four decimal places; aggregates displayed to two. Floating-point arithmetic is adequate for this case study, not a production accounting ledger.

## Time scope

Start at the first observed month if its minimum date is day 1, otherwise the next month. End at the month before the terminal observed month. This is conservative calendar coverage, not proof that no source transactions are missing. For the supplied workbook this is December 2010 through November 2011. December 2011 is available in the audit but excluded from all comparative reports. Do not compare its nine days with full months.

## Sales metrics

- **Gross merchandise sales:** sum of qualifying positive sale line values in scope.
- **Merchandise credit value:** absolute sum of qualifying negative C-invoice merchandise lines in scope.
- **Net merchandise value:** gross merchandise sales minus merchandise credit value. Excludes services and review rows; not an audited revenue or profit figure.
- **Orders:** distinct qualifying positive sale invoices. Credit-only invoices are excluded. This is a merchandise-order definition, not all invoices in the workbook.
- **Average order value:** gross merchandise sales / sale invoices.
- **Credit-to-sales value ratio:** qualifying credit value / gross sales for a product, using event dates. Not matched to purchases, may exceed 100%, and does not establish a product defect rate. Credit-only products do not appear in the sales-led product table, but their credits are included in overall/monthly totals.
- **Monthly growth:** (current gross sales − previous gross sales) / previous gross sales. First month is undefined.
- Country totals describe gross sales only. Products are grouped by StockCode; MAX(description) selects one label, not a claim that names are stable.

## Customer metrics

Customer analyses use only identified customers and qualifying positive sales in the full-month scope. Missing-ID sales remain in overall sales metrics; identified-sales share communicates coverage.

- **Repeat purchaser:** at least two distinct sale invoices in scope. Customers with multiple invoices on the same day can qualify. This overall share is not a cohort retention rate.
- **Recency:** calendar days from last observed qualifying purchase to the day after the maximum sale date in scope.
- **Frequency:** distinct qualifying sale invoices in scope.
- **Monetary:** gross qualifying sales, not credit-adjusted customer spend.
- **Spend quartile:** SQL NTILE(4), ordered by spend and customer ID for deterministic tie handling. Ties may span groups.
- **Recent:** recency <= 60 days. High-value repeat customers are repeat purchasers in the top spend quartile. One-invoice customers are grouped first regardless of recency. 'Lapsed' means no recent observed purchase, not confirmed churn.

Thresholds are illustrative, transparent business rules; they are not calibrated predictive models.

## Cohorts

Cohort = first observed qualifying purchase month within the analysis window. Denominator = identified purchasing customers first observed in that month. Numerator = distinct members of that original cohort buying in a specified subsequent month. Month 0 is 100%. Follow-up months with no purchases have 0%; months beyond observation are blank, not zero. Comparisons must account for shorter follow-up in later cohorts. Customers may have purchased before the dataset begins, so first observed is not necessarily first ever.

## Recommendations and limitations

Recommendations in findings.md are proposals motivated by descriptive results. They do not prove causes or measured impact. Source lacks product costs, original-invoice links for credits, reasons for cancellation, marketing treatment and pre-window history. One historical year cannot establish stable seasonality. Identified customer records may not be representative of unidentified purchasers.
