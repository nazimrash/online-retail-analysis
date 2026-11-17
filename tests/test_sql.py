import sqlite3
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


class SqlTests(unittest.TestCase):
    def test_credit_only_product_and_observed_zero_retention(self):
        rows = [
            ('1', '10001', 'A', 2, '2011-01-01', 5, 'a', 'UK', 10., '2011-01', 'sale', 1),
            ('2', '10001', 'A', 1, '2011-02-01', 5, 'b', 'UK', 5., '2011-02', 'sale', 1),
            ('3', '10001', 'A', 1, '2011-03-01', 5, 'a', 'UK', 5., '2011-03', 'sale', 1),
            ('C4', '99999', 'Credit only', -1, '2011-02-02', 7, 'a', 'UK', -7., '2011-02', 'credit', 1),
            ('5', '10001', 'A', 1, '2011-04-01', 5, 'c', 'UK', 5., '2011-04', 'sale', 0),
        ]
        columns = ['invoice_no', 'stock_code', 'description', 'quantity', 'invoice_date',
                   'unit_price', 'customer_id', 'country', 'line_value_gbp', 'month', 'status', 'in_analysis_window']
        with sqlite3.connect(':memory:') as con:
            pd.DataFrame(rows, columns=columns).to_sql('transactions', con, index=False)
            con.executescript((ROOT / 'sql/00_views.sql').read_text())
            overview = pd.read_sql_query((ROOT / 'sql/01_overview.sql').read_text(), con).iloc[0]
            cohorts = pd.read_sql_query((ROOT / 'sql/06_cohorts.sql').read_text(), con)
        self.assertEqual(overview.gross_sales_gbp, 20)
        self.assertEqual(overview.credit_value_gbp, 7)
        self.assertEqual(overview.net_merchandise_value_gbp, 13)
        first = cohorts[cohorts.cohort_month == '2011-01'].sort_values('month_index')
        self.assertEqual(first.retention.tolist(), [1., 0., 1.])
        later = cohorts[cohorts.cohort_month == '2011-02']
        self.assertEqual(later.month_index.tolist(), [0, 1])


if __name__ == '__main__':
    unittest.main()
