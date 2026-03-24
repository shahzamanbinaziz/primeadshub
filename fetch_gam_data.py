import pandas as pd
from googleads import ad_manager
import tempfile
import os

# 1. Configuration (We will set these in GitHub Secrets)
NETWORK_CODE = 'YOUR_NETWORK_CODE' # Your GAM Network Code
APPLICATION_NAME = 'PrimeAdsHub_Dashboard'

def run_report():
    # Load credentials from a temporary file (created from GitHub Secret)
    # For local testing, you can just point to your JSON file
    client = ad_manager.AdManagerClient.LoadFromStorage('service_account.json')
    
    report_downloader = client.GetDataService('ReportService', version='v202405')

    # 2. Define the Report
    report_job = {
        'reportQuery': {
            'dimensions': ['DATE', 'AD_UNIT_NAME', 'LINE_ITEM_NAME'],
            'columns': [
                'AD_SERVER_IMPRESSIONS', 
                'AD_SERVER_CLICKS', 
                'AD_SERVER_CTR', 
                'AD_SERVER_CPM_AND_CPC_REVENUE',
                'AD_SERVER_AVERAGE_ECPM'
            ],
            'dateRangeType': 'LAST_7_DAYS', # You can change this to LAST_30_DAYS
        }
    }

    # 3. Run and Download
    print("Starting Report Job...")
    report_job = report_downloader.runReportJob(report_job)
    
    # Wait for report to finish and download
    export_format = 'CSV_DUMP'
    report_file = tempfile.NamedTemporaryFile(suffix='.csv.gz', delete=False)
    report_downloader.downloadReport(report_job['id'], export_format, report_file)
    report_file.close()

    # 4. Process with Pandas
    df = pd.read_csv(report_file.name, compression='gzip')
    
    # Custom Metric Example: Calculate 'Net Revenue' (e.g., after 20% fee)
    df['Net_Revenue'] = df['Dimension.AD_SERVER_CPM_AND_CPC_REVENUE'] / 1000000 * 0.80
    
    # Save to CSV for the dashboard to read
    df.to_csv('gam_report_data.csv', index=False)
    print("Data fetched successfully!")

if __name__ == "__main__":
    run_report()
