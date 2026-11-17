-- RFM-style descriptive groups. Thresholds are transparent heuristics, not a trained model.
WITH reference AS (SELECT DATE(MAX(invoice_date), '+1 day') AS snapshot_date FROM sales),
customer_summary AS (
 SELECT customer_id, COUNT(DISTINCT invoice_no) AS orders, SUM(line_value_gbp) AS gross_sales_gbp,
 MIN(invoice_date) AS first_purchase, MAX(invoice_date) AS last_purchase,
 CAST(julianday(r.snapshot_date) - julianday(DATE(MAX(invoice_date))) AS INTEGER) AS recency_days
 FROM sales CROSS JOIN reference r WHERE customer_id IS NOT NULL GROUP BY customer_id
), scored AS (
 SELECT *, NTILE(4) OVER (ORDER BY gross_sales_gbp, customer_id) AS spend_quartile FROM customer_summary
)
SELECT *, CASE
 WHEN orders = 1 THEN 'One observed purchase'
 WHEN recency_days <= 60 AND spend_quartile = 4 THEN 'Recent high-value repeat'
 WHEN recency_days <= 60 THEN 'Recent repeat'
 WHEN spend_quartile = 4 THEN 'Lapsed high-value repeat'
 ELSE 'Lapsed repeat' END AS segment
FROM scored ORDER BY gross_sales_gbp DESC;
