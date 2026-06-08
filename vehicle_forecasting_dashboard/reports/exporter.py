import base64
import pandas as pd

def generate_csv_download_link(df, filename="export.csv", text="Download CSV"):
    """Generates a link to download the given dataframe as a CSV file."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="btn-download" target="_blank">{text}</a>'
    return href

def generate_pdf_report(metrics_dict, filename="report.pdf"):
    """
    Generates a textual report (as fallback for direct PDF).
    """
    summary = "Vehicle Demand Forecasting Report\n\n"
    for k, v in metrics_dict.items():
        summary += f"{k}: {v}\n"
    
    b64 = base64.b64encode(summary.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename.replace(".pdf", ".txt")}" class="btn-download" target="_blank">Download Text Summary Report</a>'
    return href
