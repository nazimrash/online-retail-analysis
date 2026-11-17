"""Rebuild the audit, SQLite analysis and reports from the original UCI workbook."""
from pathlib import Path
import argparse
import hashlib
import json
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent
COLUMNS = ['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country']


def prepare(raw):
    """Keep every original row; assign an explicit, mutually exclusive status."""
    missing = set(COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    df = raw[COLUMNS].copy()
    # Identify exact repetitions BEFORE normalisation. Keep them in the audit.
    duplicates = df.duplicated(keep='first')
    for col in ['InvoiceNo', 'StockCode', 'Description', 'CustomerID', 'Country']:
        df[col] = df[col].astype('string').str.strip().replace('', pd.NA)
    df['InvoiceNo'] = df['InvoiceNo'].str.upper()
    df['StockCode'] = df['StockCode'].str.upper()
    df['CustomerID'] = df['CustomerID'].str.replace(r'\.0$', '', regex=True)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df['source_row'] = range(2, len(df) + 2)  # Excel rows, after header
    df['is_cancellation'] = df['InvoiceNo'].str.startswith('C', na=False)
    df['is_product'] = df['StockCode'].str.fullmatch(r'\d{5}[A-Z]*', na=False)
    df['status'] = 'review'
    invalid = (df['InvoiceNo'].isna() | df['StockCode'].isna()
               | df['InvoiceDate'].isna() | df['Quantity'].isna()
               | df['UnitPrice'].isna() | ~df['Quantity'].abs().lt(float('inf'))
               | ~df['UnitPrice'].abs().lt(float('inf'))
               | df['Quantity'].mod(1).ne(0))
    valid = ~invalid & ~duplicates
    df.loc[valid & ~df['is_product'], 'status'] = 'non_product'
    df.loc[valid & df['is_product'] & df['UnitPrice'].le(0), 'status'] = 'nonpositive_price'
    eligible = valid & df['is_product'] & df['UnitPrice'].gt(0)
    df.loc[eligible & ~df['is_cancellation'] & df['Quantity'].gt(0), 'status'] = 'sale'
    df.loc[eligible & df['is_cancellation'] & df['Quantity'].lt(0), 'status'] = 'credit'
    df.loc[invalid, 'status'] = 'invalid'
    df.loc[duplicates, 'status'] = 'duplicate'
    df['line_value_gbp'] = (df['Quantity'] * df['UnitPrice']).round(4)
    df['month'] = df['InvoiceDate'].dt.strftime('%Y-%m')
    return df


def complete_months(df):
    dates = df['InvoiceDate'].dropna()
    if dates.empty:
        raise ValueError('No valid dates found.')
    start, end = dates.min(), dates.max()
    first = start.to_period('M')
    if start.day != 1:
        first += 1
    # Conservatively exclude the terminal month, even if its last date is month-end.
    # This avoids claiming complete coverage from a date range alone.
    last = end.to_period('M') - 1
    if first > last:
        raise ValueError('Need at least one full calendar month before the terminal month.')
    return [str(m) for m in pd.period_range(first, last, freq='M')]


def validate(df, months, outputs):
    sales = df[(df.status == 'sale') & df.month.isin(months)]
    credits = df[(df.status == 'credit') & df.month.isin(months)]
    k = outputs['overview'].iloc[0]
    checks = {
        'every_row_classified': bool(df.status.notna().all()),
        'sales_have_positive_quantity_and_price': bool((sales.Quantity.gt(0) & sales.UnitPrice.gt(0)).all()),
        'sales_have_no_cancellation_invoices': bool((~sales.is_cancellation).all()),
        'credits_have_negative_quantity': bool(credits.Quantity.lt(0).all()),
        'overview_sales_match_python': abs(float(k.gross_sales_gbp) - sales.line_value_gbp.sum()) < 0.02,
        'overview_credits_match_python': abs(float(k.credit_value_gbp) + credits.line_value_gbp.sum()) < 0.02,
        'sql_orders_match_python': int(k.orders) == sales.InvoiceNo.nunique(),
        'monthly_sales_reconcile': abs(outputs['monthly'].gross_sales_gbp.sum() - float(k.gross_sales_gbp)) < 0.02,
        'cohort_retention_between_zero_and_one': bool(outputs['cohorts'].retention.between(0, 1).all()),
        'cohort_month_zero_is_one': bool(outputs['cohorts'].query('month_index == 0').retention.eq(1).all()),
    }
    if not all(checks.values()):
        raise AssertionError(f'Validation failed: {checks}')
    return {key: bool(value) for key, value in checks.items()}


def write_findings(out, meta, audit):
    k = out['overview'].iloc[0]
    top = out['products'].iloc[0]
    peak = out['monthly'].sort_values('gross_sales_gbp', ascending=False).iloc[0]
    customers = out['customers']
    repeat = customers['orders'].ge(2).mean() if len(customers) else 0
    text = f'''# Analysis findings

Generated from the original workbook; not invented example results.

## Scope
- Analysis window: {meta['analysis_months'][0]} through {meta['analysis_months'][-1]}.
- Original rows: {meta['raw_rows']:,}. All original rows retained in the audit export.
- Exact duplicate rows excluded under a documented assumption: {int(audit.get('duplicate', 0)):,}.
- Customer-level results exclude unidentified customers; sales totals retain their eligible transactions.

## Results
- Gross merchandise sales: GBP {k.gross_sales_gbp:,.2f} across {int(k.orders):,} sale invoices.
- Merchandise credit value: GBP {k.credit_value_gbp:,.2f}.
- Gross sales minus merchandise credits: GBP {k.net_merchandise_value_gbp:,.2f}.
- Average gross sale invoice value: GBP {k.average_order_value_gbp:,.2f}.
- Share of gross sales with an identified customer: {k.identified_sales_share:.1%}.
- Highest gross-sales month: {peak['month']} (GBP {peak.gross_sales_gbp:,.2f}).
- Leading product by gross sales: {top.stock_code} — {top.description} (GBP {top.gross_sales_gbp:,.2f}).
- Among identified customers with purchases in the analysis window, {repeat:.1%} placed at least two sale invoices.

## Decisions these results can support
1. Review inventory planning for the leading products and high-sales periods. This single historical year is not sufficient to establish a recurring seasonal pattern.
2. Investigate products with high credit-to-sales value ratios alongside their sales volume. Credit dates do not necessarily match original purchase dates; these ratios are not matched return rates.
3. Consider a small, measurable re-engagement experiment for previously high-value customers with no recent observed purchase. Test outcomes before claiming a retention improvement.

## Limitations
No product costs, profit, cancellation reasons or marketing exposure are available. A missing later purchase does not prove churn. First observed purchase is not necessarily customer acquisition. Late cohorts have shorter follow-up. Credit invoices are not linked to original sale invoices. Product-code filtering excludes nonstandard codes and is a heuristic. Exact repetitions could represent legitimate repeated invoice lines; duplicate removal is an explicit assumption. The terminal month is excluded from comparison. The data describe a historical UK gift retailer with wholesale customers, not a current general consumer market.
'''
    (ROOT / 'reports' / 'findings.md').write_text(text, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'data/raw/Online Retail.xlsx')
    args = parser.parse_args()
    path = args.input.expanduser().resolve()
    if not path.exists():
        raise SystemExit(f'Workbook not found: {path}\nPut Online Retail.xlsx in data/raw, or use --input PATH.')
    reports = ROOT / 'reports'
    processed = ROOT / 'data/processed'
    reports.mkdir(exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    print('Reading workbook. This may take a minute...')
    raw = pd.read_excel(path, engine='openpyxl', dtype={'InvoiceNo': 'string', 'StockCode': 'string', 'CustomerID': 'string'})
    df = prepare(raw)
    months = complete_months(df)
    df['in_analysis_window'] = df.month.isin(months)
    audit = df.status.value_counts()
    audit.rename_axis('status').reset_index(name='rows').to_csv(reports / 'row_disposition.csv', index=False)
    raw.isna().sum().rename_axis('column').reset_index(name='missing_rows').to_csv(reports / 'missing_values.csv', index=False)
    df.to_csv(processed / 'audited_transactions.csv', index=False)
    db_path = processed / 'retail.sqlite'
    sql_frame = df.rename(columns={
        'InvoiceNo': 'invoice_no', 'StockCode': 'stock_code', 'Description': 'description',
        'Quantity': 'quantity', 'InvoiceDate': 'invoice_date', 'UnitPrice': 'unit_price',
        'CustomerID': 'customer_id', 'Country': 'country'})
    with sqlite3.connect(db_path) as con:
        con.executescript('DROP VIEW IF EXISTS sales; DROP VIEW IF EXISTS credits;')
        sql_frame.to_sql('transactions', con, index=False, if_exists='replace')
        con.executescript((ROOT / 'sql/00_views.sql').read_text())
        outputs = {}
        for sql_file in sorted((ROOT / 'sql').glob('[0-9][0-9]_*.sql')):
            if sql_file.name.startswith('00_'):
                continue
            name = sql_file.stem[3:]
            outputs[name] = pd.read_sql_query(sql_file.read_text(), con)
            outputs[name].to_csv(reports / f'{name}.csv', index=False)
    checks = validate(df, months, outputs)
    meta = {
        'dataset': 'UCI Online Retail', 'source': 'https://archive.ics.uci.edu/dataset/352/online-retail',
        'raw_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'raw_rows': len(raw),
        'raw_start': str(df.InvoiceDate.min()), 'raw_end': str(df.InvoiceDate.max()),
        'analysis_months': months, 'pandas_version': pd.__version__,
        'row_disposition': {str(k): int(v) for k, v in audit.items()}, 'validation': checks,
    }
    (reports / 'run_metadata.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    write_findings(outputs, meta, audit)
    print(f'Done. {len(raw):,} rows audited; {sum(checks.values())} validation checks passed.')
    print(f'Analysis: {months[0]} to {months[-1]}')
    print(f'Reports: {reports}')
    print('Launch dashboard: python -m streamlit run dashboard.py')


if __name__ == '__main__':
    main()
