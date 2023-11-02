import streamlit as st
import pandas as pd
from pages import page1

st.set_page_config(page_title="Multi-Page App")

st.title("Welcome to the Multi-Page Streamlit App")

# Upload DataFrame and YAML file in the main script
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
reference_file = st.file_uploader("Upload YAML file with reference columns (optional)", type=["yml", "yaml"])

# Initialize DataFrame and reference_columns
df = None
reference_columns = []

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    if reference_file is not None:
        with reference_file as file:
            try:
                reference_columns = yaml.safe_load(file)
            except Exception as e:
                st.error(f"Error loading reference columns: {str(e)}")

# Pass data to Page 1
if df is not None:
    page1.page_1(df, reference_columns)
