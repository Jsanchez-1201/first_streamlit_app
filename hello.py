import streamlit as st
import pandas as pd
import yaml
from pages import page1

st.set_page_config(page_title="Multi-Page App")

st.title("Welcome to the Marketing Data Cleaning App")

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

# Pass data to Page 1 using st.session_state
st.session_state.df = df
st.session_state.reference_columns = reference_columns

# If the user clicks the button to use default YAML, load the standard_columns.yml
if st.button("Continue with Default YAML"):
    with open('standard_columns.yml', 'r') as default_yaml:
        st.session_state.reference_columns = yaml.safe_load(default_yaml)

# Redirect to Page 1 only if data exists
if st.session_state.df is not None:
    page1.page_1()









