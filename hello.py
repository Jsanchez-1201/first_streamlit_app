import streamlit as st
import pandas as pd
import fuzzywuzzy.process as fuzz
import re
import yaml

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

if st.button("Continue with Default YAML"):
    st.session_state.df = df
    st.session_state.reference_columns = reference_columns
    st.session_state.default_yaml = True

if not hasattr(st.session_state, 'df'):
    st.session_state.df = None
if not hasattr(st.session_state, 'reference_columns'):
    st.session_state.reference_columns = None
if not hasattr(st.session_state, 'default_yaml'):
    st.session_state.default_yaml = False

if st.session_state.df is not None:
    if st.session_state.default_yaml:
        st.write("Using the default YAML.")
    else:
        st.write("Using the uploaded YAML.")
