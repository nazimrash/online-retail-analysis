-- Cohorts use FIRST OBSERVED purchase month in the analysis window, not acquisition date.
WITH active AS (
 SELECT DISTINCT customer_id, month FROM sales WHERE customer_id IS NOT NULL
), first_month AS (
 SELECT customer_id, MIN(month) AS cohort_month FROM active GROUP BY customer_id
), sizes AS (
 SELECT cohort_month, COUNT(*) AS cohort_size FROM first_month GROUP BY cohort_month
), counts AS (
 SELECT f.cohort_month, a.month AS activity_month,
 (CAST(substr(a.month, 1, 4) AS INTEGER) - CAST(substr(f.cohort_month, 1, 4) AS INTEGER)) * 12
 + CAST(substr(a.month, 6, 2) AS INTEGER) - CAST(substr(f.cohort_month, 6, 2) AS INTEGER) AS month_index,
 COUNT(*) AS active_customers
 FROM active a JOIN first_month f USING(customer_id) GROUP BY f.cohort_month, a.month
), horizon AS (SELECT MAX(month) AS last_month FROM sales),
calendar AS (SELECT DISTINCT month FROM sales), grid AS (
 SELECT s.cohort_month, s.cohort_size, m.month AS activity_month,
 (CAST(substr(m.month, 1, 4) AS INTEGER) - CAST(substr(s.cohort_month, 1, 4) AS INTEGER)) * 12
 + CAST(substr(m.month, 6, 2) AS INTEGER) - CAST(substr(s.cohort_month, 6, 2) AS INTEGER) AS month_index
 FROM sizes s CROSS JOIN calendar m CROSS JOIN horizon h
 WHERE m.month >= s.cohort_month AND m.month <= h.last_month
)
SELECT g.*, COALESCE(c.active_customers, 0) AS active_customers,
 1.0 * COALESCE(c.active_customers, 0) / g.cohort_size AS retention
FROM grid g LEFT JOIN counts c USING(cohort_month, activity_month, month_index)
ORDER BY cohort_month, month_index;
