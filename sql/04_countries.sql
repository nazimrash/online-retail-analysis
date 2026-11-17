SELECT COALESCE(country, 'Unknown') AS country, ROUND(SUM(line_value_gbp), 2) AS gross_sales_gbp,
 COUNT(DISTINCT invoice_no) AS orders, COUNT(DISTINCT customer_id) AS identified_customers
FROM sales GROUP BY COALESCE(country, 'Unknown') ORDER BY gross_sales_gbp DESC;
