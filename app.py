import streamlit as st
import pandas as pd
import plotly.express as px
from googleads import ad_manager
import tempfile
import os
import json

# --- CONFIGURATION ---
NETWORK_CODE = '23327488191'
KEY_DATA = {
  "type": "service_account",
  "project_id": "prime-ads-hub",
  "private_key_id": "e9ea45e55a74cc1e56f91ed0d0e11961e20d7682",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6CU7PPyKw5elT\nhbzUUYzw4FUjnY9yWtQ7GBADIlHI9nlXBxQUh9WctzlbH5NmfOF0grk5mnQqD87B\ne/8OPto7vESUL7c4PdOLE94LzddHszppI2fybx5Glk7olW4+0/5hd3A/wx8hr0D7\ndCxWV1kfofvgm+fGqCdtSBteeTL4cCKIBArHW07FZVbU7xR+SipbEkldZF/X09ol\nc9SAwyxO7uLwVGdQAIxGfT1DZ2IrkVNUJofCCTZqc/YY1dQgdewu4QUXEUXZwVv9\nQ++2TL4rkp24ygiPCChRAaDgM4fxmWIu0L13QNms6HVucqpeBkRUVRx/cqt0GKUm\nCjFDQNxdAgMBAAECggEAFuT22Svup8D/lCsI+EMZ+nnNGH83LE5PwH7/V3dlg7sL\nZ0Gkf7tQt0LYMOXjpLD5KPa+dz+SDKwZ2HdbReRHxKKweOEfZfE746l8Ac1g8T62\nEULNc8kne23bg6WCJgK+Uz3Y50vqvKE9+MQNAcopmmo7nmJpZWoDwh/l2FxHgMnM\nErO8Cn5vaIQKGmYX+zNTkeGZKTndhll8ZN5iyD1BD3nIyMWqQhYqKeBYBTOO3XXf\nMdf+OkrjeLRQpZQwdq1wWyAQlNz7hFLl4n7TgBDjFmGCTrfRlBXt0EJI2pLlRiI/\n2xbPLGkT7XEVoeuxkwIW16K9hhRhEZ0OCKYXbw7cAQKBgQDu9bmn0VwqTciRnpkt\n2ypxrUiT7zuMxCdDg/7x3z064HqRTHLkmen8/3bG5ebxwd1SUkiZpzjqWUNP12Qh\n9ITLotzENgMOWX3yPRDVRkO5+uYwVcVLcuzPcajxglX8pWVa+j472EPvKE5UY/Ca\n01UnQOQkbE3c8ZjDYWLwFi54XQKBgQDHTXNA4zToNVKejbRj3MehmLLUeIOgvI9z\nRIylioynnj7bzrOGUmA5DSk0z3tHcUYYbOZg/52jS/Uhsz/IH/Z1ZZatMqz/YYZX\nLXxKXLltuIfGtP5tvoKOfDMv8ENsDDBIdE+mtiSfFaiXvJzp8imlsst/YIIEhoLI\nE0GX1yW0AQKBgDzdoCVrwVMRLvZQdGnmuj/sSGFN/VgUmn+q/mQzXZBCn1WlKFqs\ DZqgo2t0IcgQfkQ6qz1gB7JBfFC450ty0eRgnmTn8Q1VpCvwe/onBJc5nipPnopi\nQolwRP0HGsnYgyGSPgnWQy+Gj7UVI7L8A2OVNsdEQuz1KNkTVDUdIUcNAoGALmXI\ndA2w7nIjdsf0e98VFnivASnBMvVSy/nkaFF15zu+1HstbhLVVdLLigDXaU1kjSEl\nDOXVNAPl4F+TdKqEPNZWmqGWhqmUlc0AB2vIu1NfQJI4PSJB0Jv3aqybdZbs0qFJ\nPb1fjy2CnziIqyn2Kh4So+e6vQT3g06AUbIDlAECgYEA1uExESpqYjifKW4ZKfCa\nm3RYDs0FNITiC/tU+i3m+4pCtbjKqcb4HimivEUPdx2Eh8xZlOQ+nWNEQkg72yiH\n5nksFlo3xaLQwNk+7wmvxufZAPt32Y75eju6MlteOwYGXPibFzqUusHyYQ3kRycV\nwX8a+qHII56+6MGt4y1HV0s=\n-----END PRIVATE KEY-----\n",
  "client_email": "prime-ads-hub@prime-ads-hub.iam.gserviceaccount.com",
}

st.set_page_config(page_title="Prime Ads Hub | Dashboard", layout="wide")

# --- DATA FETCHING ---
@st.cache_data(ttl=10800)  # Auto-refresh every 3 hours
def get_gam_data():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        json.dump(KEY_DATA, tmp)
        tmp_path = tmp.name

    try:
        client = ad_manager.AdManagerClient.LoadFromStorage(tmp_path)
        client.network_code = NETWORK_CODE
        report_downloader = client.GetDataService('ReportService', version='v202408')

        report_job = {
            'reportQuery': {
                'dimensions': ['DATE', 'AD_UNIT_NAME'],
                'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS', 'AD_SERVER_CPM_AND_CPC_REVENUE'],
                'dateRangeType': 'LAST_7_DAYS',
            }
        }
        
        report_job = report_downloader.runReportJob(report_job)
        report_file = tempfile.NamedTemporaryFile(suffix='.csv.gz', delete=False)
        report_downloader.downloadReport(report_job['id'], 'CSV_DUMP', report_file)
        report_file.close()

        df = pd.read_csv(report_file.name, compression='gzip')
        df['Revenue'] = df['Column.AD_SERVER_CPM_AND_CPC_REVENUE'] / 1000000
        return df
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- UI DESIGN ---
st.title("🚀 Prime Ads Hub Reporting Hub")
st.sidebar.header("Settings")
if st.sidebar.button("Force Update Now"):
    st.cache_data.clear()
    st.rerun()

try:
    with st.spinner('Accessing Google Ad Manager...'):
        data = get_gam_data()

    # Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Revenue", f"${data['Revenue'].sum():,.2f}")
    m2.metric("Total Impressions", f"{data['Column.AD_SERVER_IMPRESSIONS'].sum():,}")
    m3.metric("Avg CTR", f"{(data['Column.AD_SERVER_CLICKS'].sum()/data['Column.AD_SERVER_IMPRESSIONS'].sum()*100):,.2f}%")

    # Chart
    st.subheader("Revenue Trend")
    fig = px.area(data, x='Dimension.DATE', y='Revenue', color='Dimension.AD_UNIT_NAME', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.subheader("Detailed Report")
    st.dataframe(data, use_container_width=True)

except Exception as e:
    st.error("⚠️ Connection Error")
    st.write(f"**Details:** {e}")
    st.info("Please ensure the Service Account email is added as a USER in your GAM settings.")
