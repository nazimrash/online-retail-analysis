-- Full-month merchandise scope shared by all report queries.
CREATE INDEX IF NOT EXISTS idx_scope ON transactions(status, in_analysis_window);
CREATE INDEX IF NOT EXISTS idx_customer ON transactions(customer_id, invoice_date);
CREATE VIEW sales AS
SELECT * FROM transactions WHERE status = 'sale' AND in_analysis_window = 1;
CREATE VIEW credits AS
SELECT * FROM transactions WHERE status = 'credit' AND in_analysis_window = 1;
