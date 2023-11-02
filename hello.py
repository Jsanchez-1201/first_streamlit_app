import streamlit as st
import pandas as pd
import fuzzywuzzy.process as fuzz
import re
import yaml

# Function to find and match columns
def match_columns(df, reference_columns):
    matched_columns = {}  # Initialize the matched_columns dictionary

    input_columns = df.columns.tolist()

    for column in input_columns:
        matches = fuzz.extractBests(column, reference_columns)
        if matches:
            matched_columns[column] = matches

    return matched_columns

# Page 1: Upload DataFrame and YAML File
def page_1():
    st.title('Page 1: Upload DataFrame and YAML File')

    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    reference_columns = []  # Default reference columns, change this list as needed

    default_yaml = "standard_columns.yml"  # Default YAML file for reference columns
    try:
        with open(default_yaml, 'r') as default_yaml_file:
            reference_columns = yaml.safe_load(default_yaml_file)
    except Exception as e:
        st.warning(f"Using default reference columns. Error loading default YAML file: {str(e)}")

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.subheader('Data Preview:')
            st.write(df)

            reference_file = st.file_uploader("Upload YAML file with reference columns (optional)", type=["yml", "yaml"])

            if reference_file is not None:
                with reference_file as file:
                    try:
                        reference_columns = yaml.safe_load(file)
                    except Exception as e:
                        st.error(f"Error loading reference columns: {str(e)}")
                        reference_columns = []

            st.write("You can now navigate to Page 2 to perform column mapping and data cleaning.")

            st.write("Or you can upload a different Excel file and YAML file on this page.")

# Page 2: Column Mapping and Data Cleaning
def page_2():
    st.title('Page 2: Column Mapping and Data Cleaning')

    # Load DataFrame and reference columns
    if 'df' not in st.session_state:
        st.write("Please upload your DataFrame and YAML file on Page 1.")
        return

    df = st.session_state.df
    reference_columns = st.session_state.reference_columns

    if reference_columns:
        matched_columns = match_columns(df, reference_columns)

        mapped_columns_text = ""
        for column_index, (column, mapping) in enumerate(matched_columns.items()):
            mapped_columns_text += f"{column_index}. '{column}' is initially mapped to '{mapping[0][0]}'\n"

        st.text(mapped_columns_text)

        # Allow the user to specify columns for modification
        st.subheader('Column Modification')
        change_columns_input = st.text_input("Enter a list of columns to modify (e.g., '0, 1, 2') or 'none' to skip:", key='change_columns_input')

        if change_columns_input.lower() != 'none':
            change_columns_list = [int(col.strip()) for col in change_columns_input.split(',') if col.strip()]
            for column_index in change_columns_list:
                if 0 <= column_index < len(matched_columns):
                    selected_column = list(matched_columns.keys())[column_index]
                    st.write(f"Mapping options for column {column_index}: '{selected_column}':")
                    for j, (match, score) in enumerate(matched_columns[selected_column]):
                        st.write(f"  {j}. Map to '{match}' (Score: {score})")  # Display all mapping options
                    match_choice = st.text_input("Enter the number for the mapping, or 'skip' to keep as is:", key=f'match_choice_{column_index}')
                    if match_choice.lower() != 'skip' and match_choice.isdigit():
                        match_index = int(match_choice)
                        if 0 <= match_index < len(matched_columns[selected_column]):
                            chosen_mapping = matched_columns[selected_column][match_index][0]
                            df.rename(columns={selected_column: chosen_mapping}, inplace=True)
                            st.write(f"Column {column_index}: '{selected_column}' has been mapped to '{chosen_mapping}'.")
                    else:
                        st.write("No changes have been made to the column.")

        # Remove columns that are not in reference_columns in the updated DataFrame
        columns_to_remove = [col for col in df.columns if col not in reference_columns]
        df.drop(columns=columns_to_remove, inplace=True)
        # Check if "Last Name" doesn't exist and create it
        if "Last Name" not in df.columns:
            df["Last Name"] = ""
        st.subheader('Updated DataFrame:')
        st.write(df)

# Main app
if 'page' not in st.session_state:
    st.session_state.page = 1

if st.session_state.page == 1:
    page_1()
else:
    page_2()
