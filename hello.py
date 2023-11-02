import streamlit as st
import pandas as pd
import yaml
from pages import page1

st.set_page_config(page_title="Multi-Page App")

st.title("Welcome to the Multi-Page Streamlit App")

# Unique keys for file upload widgets
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"], key="excel_uploader")
reference_file = st.file_uploader("Upload YAML file with reference columns (optional)", type=["yml", "yaml"], key="yaml_uploader")

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

# Use st.cache to persist data between pages
cached_data = st.cache(allow_output_mutation=True)(lambda: {"df": None, "reference_columns": []})
data = cached_data()

# Store data
data["df"] = df
data["reference_columns"] = reference_columns

# Check if Page 1 is started
if not "page_1_started" in st.session_state:
    st.session_state.page_1_started = False

if not st.session_state.page_1_started:
    if st.button("Continue with Default YAML"):
        st.session_state.page_1_started = True
        st.title("Page 1: Automated and Manual Column Mapping")

# If Page 1 is started, execute Page 1
if st.session_state.page_1_started:
    page1.page_1(data["df"], data["reference_columns"])
