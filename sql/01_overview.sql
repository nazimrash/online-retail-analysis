-- Credits are separate events, not matched returns from these sale invoices.
WITH s AS (
 SELECT SUM(line_value_gbp) AS gross_sales_gbp, COUNT(DISTINCT invoice_no) AS orders,
        COUNT(DISTINCT customer_id) AS identified_customers,
        SUM(CASE WHEN customer_id IS NOT NULL THEN line_value_gbp ELSE 0 END) AS identified_sales
 FROM sales
), c AS (SELECT COALESCE(-SUM(line_value_gbp), 0) AS credit_value_gbp FROM credits)
SELECT ROUND(s.gross_sales_gbp, 2) AS gross_sales_gbp, s.orders, s.identified_customers,
 ROUND(c.credit_value_gbp, 2) AS credit_value_gbp,
 ROUND(s.gross_sales_gbp - c.credit_value_gbp, 2) AS net_merchandise_value_gbp,
 ROUND(s.gross_sales_gbp / NULLIF(s.orders, 0), 2) AS average_order_value_gbp,
 s.identified_sales / NULLIF(s.gross_sales_gbp, 0) AS identified_sales_share
FROM s CROSS JOIN c;
