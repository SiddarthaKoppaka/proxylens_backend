import pandas as pd
from langchain_community.document_loaders import WebBaseLoader

# Load metadata CSV
metadata_df = pd.read_csv("src/db/metadata.csv")

def fetch_html_content(url):
    """Fetch and extract text from a webpage using LangChain's WebBaseLoader."""
    if not isinstance(url, str) or not url.startswith("http"):
        return None  # Return None if the URL is invalid

    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        extracted_text = "\n".join([doc.page_content for doc in docs])
        return extracted_text[:5000]  # Limit content to avoid overloading the model
    except Exception as e:
        print(f"Error fetching HTML content from {url}: {e}")
        return None

def lookup_metadata(query):
    """Search the metadata CSV for relevant company information and reports."""
    results = metadata_df[metadata_df["conm"].str.contains(query, case=False, na=False)]

    if results.empty:
        return None

    extracted_data = []
    for _, row in results.iterrows():
        metadata_info = {
            "company": row["conm"],
            "gvkey": row["gvkey"],
            "gvkey6": row["gvkey6"],
            "datadate": row["datadate"],
            "fyear": row["fyear"],
            "ticker": row["tic"],
            "cusip": row["cusip"],
            "cik": row["cik"],
            "sic": row["sic"],
            "sale": row["sale"],
            "financial_year": row["fyear"],
        }

        # Try fetching reports from the primary links
        annual_report_text = fetch_html_content(row["annualreport"]) if "annualreport" in row and pd.notna(row["annualreport"]) else None
        proxy_statement_text = fetch_html_content(row["proxystatement"]) if "proxystatement" in row and pd.notna(row["proxystatement"]) else None

        # Fallback to search links if the primary links fail
        if not annual_report_text and "annualreportsearch" in row and pd.notna(row["annualreportsearch"]):
            annual_report_text = fetch_html_content(row["annualreportsearch"])

        if not proxy_statement_text and "proxystatementsearch" in row and pd.notna(row["proxystatementsearch"]):
            proxy_statement_text = fetch_html_content(row["proxystatementsearch"])

        # Store the extracted data
        metadata_info["annual_report"] = annual_report_text
        metadata_info["proxy_statement"] = proxy_statement_text

        extracted_data.append(metadata_info)

    return extracted_data




# import pandas as pd
# from langchain_community.document_loaders import WebBaseLoader

# class CompanyMetadataFetcher:
#     def __init__(self, metadata_csv_path):
#         """
#         Initialize the metadata fetcher with a CSV file containing company metadata.
#         """
#         self.metadata_df = pd.read_csv(metadata_csv_path)

#     @staticmethod
#     def fetch_html_content(url):
#         """
#         Fetch and extract text from a webpage using LangChain's WebBaseLoader.
#         """
#         if not isinstance(url, str) or not url.startswith("http"):
#             return None  # Return None if the URL is invalid

#         try:
#             loader = WebBaseLoader(url)
#             docs = loader.load()
#             extracted_text = "\n".join([doc.page_content for doc in docs])
#             return extracted_text[:5000]  # Limit content to avoid overloading the model
#         except Exception as e:
#             print(f"Error fetching HTML content from {url}: {e}")
#             return None

#     def lookup_metadata(self, query):
#         """
#         Search the metadata CSV for relevant company information and reports.
#         """
#         results = self.metadata_df[self.metadata_df["conm"].str.contains(query, case=False, na=False)]

#         if results.empty:
#             return None

#         extracted_data = []
#         for _, row in results.iterrows():
#             metadata_info = {
#                 "company": row["conm"],
#                 "gvkey": row["gvkey"],
#                 "gvkey6": row["gvkey6"],
#                 "datadate": row["datadate"],
#                 "fyear": row["fyear"],
#                 "ticker": row["tic"],
#                 "cusip": row["cusip"],
#                 "cik": row["cik"],
#                 "sic": row["sic"],
#                 "sale": row["sale"],
#                 "financial_year": row["fyear"],
#             }

#             # Fetch reports from primary links
#             annual_report_text = self.fetch_html_content(row["annualreport"]) if "annualreport" in row and pd.notna(row["annualreport"]) else None
#             proxy_statement_text = self.fetch_html_content(row["proxystatement"]) if "proxystatement" in row and pd.notna(row["proxystatement"]) else None

#             # Fallback to search links if primary links fail
#             if not annual_report_text and "annualreportsearch" in row and pd.notna(row["annualreportsearch"]):
#                 annual_report_text = self.fetch_html_content(row["annualreportsearch"])

#             if not proxy_statement_text and "proxystatementsearch" in row and pd.notna(row["proxystatementsearch"]):
#                 proxy_statement_text = self.fetch_html_content(row["proxystatementsearch"])

#             # Store extracted data
#             metadata_info["annual_report"] = annual_report_text
#             metadata_info["proxy_statement"] = proxy_statement_text

#             extracted_data.append(metadata_info)

#         return extracted_data
