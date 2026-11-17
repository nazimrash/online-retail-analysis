"""Small regression checks for classification and exclusions; no external data needed."""
import unittest
import pandas as pd
from retail_pipeline import prepare


class ClassificationTests(unittest.TestCase):
    def test_sales_credits_missing_customer_and_exceptions(self):
        base = {'InvoiceNo': '100001', 'StockCode': '85123A', 'Description': 'Gift',
                'Quantity': 2, 'InvoiceDate': '2011-01-01', 'UnitPrice': 3.5,
                'CustomerID': '12345', 'Country': 'United Kingdom'}
        variations = [{}, {'InvoiceNo': 'C100002', 'Quantity': -2},
                      {'InvoiceNo': '100003', 'CustomerID': None},
                      {'InvoiceNo': '100004', 'StockCode': 'POST'},
                      {'InvoiceNo': '100005', 'Quantity': -1},
                      {'InvoiceNo': 'C100006', 'Quantity': 1},
                      {'InvoiceNo': '100007', 'UnitPrice': 0},
                      {'InvoiceNo': '100008', 'InvoiceDate': 'bad date'}, {}]
        result = prepare(pd.DataFrame([base | change for change in variations]))
        self.assertEqual(result.status.tolist(), ['sale', 'credit', 'sale', 'non_product',
                                                  'review', 'review', 'nonpositive_price', 'invalid', 'duplicate'])
        self.assertTrue(pd.isna(result.loc[2, 'CustomerID']))
        self.assertEqual(result.loc[0, 'line_value_gbp'], 7)
        self.assertEqual(result.loc[1, 'line_value_gbp'], -7)


if __name__ == '__main__':
    unittest.main()
