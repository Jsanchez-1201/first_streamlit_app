import streamlit as st
import pandas as pd
import yaml  # Import the yaml library
from pages import page1  # Import your custom page

st.set_page_config(page_title="Multi-Page App")

st.title("Welcome to the Marketing Data Cleaning App")

# Unique keys for file upload widgets
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"], key="excel_uploader")
reference_file = st.file_uploader("Upload YAML file with reference columns (optional)", type=["yml", "yaml"], key="yaml_uploader")

# Initialize DataFrame and reference_columns
df = None
reference_columns = []

# Pre-load the standard_columns.yml
with open('standard_columns.yml', 'r') as default_yaml:
    default_reference_columns = yaml.safe_load(default_yaml)

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

# Redirect to Page 1
if st.session_state.df is not None and st.session_state.reference_columns:
    page1.page_1()

# Add a button to continue with the default yaml
if st.button("Continue with Default YAML"):
    st.session_state.df = df
    st.session_state.reference_columns = default_reference_columns  # Assign the pre-loaded default YAML
    page1.page_1()
