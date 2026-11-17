WITH s AS (
 SELECT stock_code, MAX(description) AS description, SUM(quantity) AS units,
 SUM(line_value_gbp) AS gross_sales_gbp, COUNT(DISTINCT invoice_no) AS orders
 FROM sales GROUP BY stock_code
), c AS (
 SELECT stock_code, -SUM(line_value_gbp) AS credit_value_gbp FROM credits GROUP BY stock_code
)
SELECT s.*, ROUND(COALESCE(c.credit_value_gbp, 0), 2) AS credit_value_gbp,
 COALESCE(c.credit_value_gbp, 0) / NULLIF(s.gross_sales_gbp, 0) AS credit_to_sales_value_ratio
FROM s LEFT JOIN c USING(stock_code) ORDER BY gross_sales_gbp DESC;
