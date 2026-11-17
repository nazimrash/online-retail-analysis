WITH s AS (
 SELECT month, SUM(line_value_gbp) AS gross_sales_gbp, COUNT(DISTINCT invoice_no) AS orders
 FROM sales GROUP BY month
), c AS (
 SELECT month, -SUM(line_value_gbp) AS credit_value_gbp FROM credits GROUP BY month
), months AS (SELECT month FROM s UNION SELECT month FROM c), totals AS (
 SELECT m.month, ROUND(COALESCE(s.gross_sales_gbp, 0), 2) AS gross_sales_gbp,
 COALESCE(s.orders, 0) AS orders, ROUND(COALESCE(c.credit_value_gbp, 0), 2) AS credit_value_gbp
 FROM months m LEFT JOIN s USING(month) LEFT JOIN c USING(month)
), previous AS (
 SELECT *, LAG(gross_sales_gbp) OVER (ORDER BY month) AS previous_month_sales FROM totals
)
SELECT *, ROUND(gross_sales_gbp - credit_value_gbp, 2) AS net_merchandise_value_gbp,
 (gross_sales_gbp - previous_month_sales) / NULLIF(previous_month_sales, 0) AS sales_growth
FROM previous ORDER BY month;
