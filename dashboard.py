"""Local, read-only dashboard for reports produced by retail_pipeline.py."""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / 'reports'
st.set_page_config(page_title='Retail | Sales & Customers', page_icon='📊', layout='wide')
st.title('Retail sales & customer retention')
st.caption('Historical UCI Online Retail case study • GBP • SQL-backed reporting')
if not (REPORTS / 'run_metadata.json').exists():
    st.info('First run: python retail_pipeline.py')
    st.stop()
meta = json.loads((REPORTS / 'run_metadata.json').read_text())


def read(name):
    return pd.read_csv(REPORTS / f'{name}.csv')


k = read('overview').iloc[0]
monthly = read('monthly')
products = read('products')
customers = read('customers')
cohorts = read('cohorts')
st.info(f"Complete-month scope: {meta['analysis_months'][0]} to {meta['analysis_months'][-1]}. "
        'The terminal month is excluded. Credits are not matched to original sale invoices.')
cols = st.columns(4)
cols[0].metric('Gross merchandise sales', f"£{k.gross_sales_gbp:,.0f}")
cols[1].metric('Merchandise credits', f"£{k.credit_value_gbp:,.0f}")
cols[2].metric('Sale invoices', f'{int(k.orders):,}')
cols[3].metric('Average gross invoice', f'£{k.average_order_value_gbp:,.2f}')
sales_tab, customer_tab, quality_tab = st.tabs(['Sales performance', 'Customers & retention', 'Data quality & findings'])
with sales_tab:
    st.subheader('Monthly performance')
    measure = st.selectbox('Monthly measure', ['gross_sales_gbp', 'net_merchandise_value_gbp', 'credit_value_gbp', 'orders'])
    fig = px.line(monthly, x='month', y=measure, markers=True,
                  labels={'month': 'Month', measure: measure.replace('_', ' ').title()})
    fig.update_traces(line_color='#2563eb')
    st.plotly_chart(fig, width='stretch')
    left, right = st.columns(2)
    with left:
        limit = st.slider('Number of leading products', 5, 25, 10)
        p = products.head(limit).sort_values('gross_sales_gbp')
        st.plotly_chart(px.bar(p, x='gross_sales_gbp', y='stock_code', orientation='h',
                              hover_data=['description'], title='Leading products by gross sales',
                              labels={'gross_sales_gbp': 'Gross sales (£)', 'stock_code': 'Product code'}), width='stretch')
    with right:
        countries = read('countries')
        exclude_uk = st.checkbox('Exclude UK from country chart', value=True)
        if exclude_uk:
            countries = countries[countries.country != 'United Kingdom']
        st.plotly_chart(px.bar(countries.head(10).sort_values('gross_sales_gbp'), x='gross_sales_gbp',
                              y='country', orientation='h', title='Leading countries',
                              labels={'gross_sales_gbp': 'Gross sales (£)', 'country': 'Country'}), width='stretch')
    st.subheader('Products to investigate')
    threshold = st.number_input('Minimum gross product sales (£)', min_value=0, value=1000, step=250)
    review = products[products.gross_sales_gbp >= threshold].sort_values('credit_to_sales_value_ratio', ascending=False)
    st.caption('Credit-to-sales value ratio is not a matched return rate. Ratios may exceed 100%.')
    st.dataframe(review.head(20), hide_index=True, width='stretch')
    st.download_button('Download monthly SQL results', monthly.to_csv(index=False), 'monthly.csv', 'text/csv')
with customer_tab:
    a, b, c = st.columns(3)
    a.metric('Identified purchasing customers', f'{len(customers):,}')
    b.metric('Repeat purchasers', f"{customers.orders.ge(2).mean():.1%}" if len(customers) else 'N/A')
    c.metric('Sales linked to customer IDs', f'{k.identified_sales_share:.1%}')
    st.caption('Repeat purchaser = at least two distinct sale invoices within the selected full-month scope. '
               'All customer figures below use the same fixed window; they do not change with sales chart controls.')
    grouped = customers.groupby('segment', as_index=False).agg(customers=('customer_id', 'count'), sales=('gross_sales_gbp', 'sum'))
    st.plotly_chart(px.bar(grouped, x='customers', y='segment', orientation='h', color='segment',
                          title='Descriptive customer groups'), width='stretch')
    st.caption('Recent = last observed purchase within 60 days of the day after the final sale in scope. '
               'High value = top spend quartile. One-purchase customers are grouped separately. These are heuristics, not churn predictions.')
    st.subheader('Monthly cohort retention')
    if not cohorts.empty:
        matrix = cohorts.pivot(index='cohort_month', columns='month_index', values='retention')
        heat = px.imshow(matrix, text_auto='.0%', aspect='auto', color_continuous_scale='Blues',
                         zmin=0, zmax=1, labels={'x': 'Months since first observed purchase', 'y': 'First observed purchase month', 'color': 'Retention'})
        st.plotly_chart(heat, width='stretch')
    st.caption('Each cell is the share of the original cohort purchasing in that month. '
               'Blank cells have not been observed; 0% means observed with no repeat purchases. '
               'First observed purchase does not prove acquisition. No customer identities are displayed.')
with quality_tab:
    left, right = st.columns(2)
    with left:
        st.subheader('Every source row accounted for')
        st.dataframe(read('row_disposition'), hide_index=True, width='stretch')
    with right:
        st.subheader('Missing values before cleaning')
        st.dataframe(read('missing_values'), hide_index=True, width='stretch')
    st.subheader('Validation')
    st.dataframe(pd.DataFrame([{'check': key, 'passed': value} for key, value in meta['validation'].items()]), hide_index=True)
    st.markdown((REPORTS / 'findings.md').read_text())
    st.caption('Source: Chen, D. (2015). Online Retail. UCI Machine Learning Repository. '
               'https://doi.org/10.24432/C5BW33 • CC BY 4.0')
