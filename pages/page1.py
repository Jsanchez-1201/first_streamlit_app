import streamlit as st
import pandas as pd
import yaml
import fuzzywuzzy.process as fuzz

# Function to find and match columns
def match_columns(df, reference_columns):
    matched_columns = {}  # Initialize the matched_columns dictionary

    input_columns = df.columns.tolist()

    for column in input_columns:
        matches = fuzz.extractBests(column, reference_columns)
        if matches:
            matched_columns[column] = matches

    return matched_columns

# Page 1: Upload DataFrame and Initial Mapping
def page_1():
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.subheader('Data Preview:')
        st.write(df)

        reference_columns = []  # Default reference columns, change this list as needed
        default_yaml = "standard_columns.yml"  # Default YAML file for reference columns

        reference_file = st.file_uploader("Upload YAML file with reference columns (optional)", type=["yml", "yaml"])

        if reference_file is not None:
            with reference_file as file:
                try:
                    reference_columns = yaml.safe_load(file)
                except Exception as e:
                    st.error(f"Error loading reference columns: {str(e)}")
                    reference_columns = []

        if reference_columns:
            matched_columns = match_columns(df, reference_columns)

            st.subheader('Mapped Columns:')
            mapped_columns_text = ""
            for column_index, (column, mapping) in enumerate(matched_columns.items()):
                mapped_columns_text += f"{column_index}. '{column}' is initially mapped to '{mapping[0][0]}'\n"

            st.text(mapped_columns_text)

            # Allow the user to specify columns for modification
            st.subheader('Column Modification')
            change_columns_input = st.text_input("Enter a list of columns to modify (e.g., '0, 1, 2') or 'none' to skip:")

            if change_columns_input.lower() != 'none':
                change_columns_list = [int(col.strip()) for col in change_columns_input.split(',') if col.strip()]
                for column_index in change_columns_list:
                    if 0 <= column_index < len(matched_columns):
                        selected_column = list(matched_columns.keys())[column_index]
                        st.write(f"Mapping options for column {column_index}: '{selected_column}':")
                        for j, (match, score) in enumerate(matched_columns[selected_column]):
                            st.write(f"  {j}. Map to '{match}' (Score: {score})")  # Display all mapping options
                        match_choice = st.text_input("Enter the number for the mapping, or 'skip' to keep as is:")
                        if match_choice.lower() != 'skip' and match_choice.isdigit():
                            match_index = int(match_choice)
                            if 0 <= match_index < len(matched_columns[selected_column]):
                                chosen_mapping = matched_columns[selected_column][match_index][0]
                                df.rename(columns={selected_column: chosen_mapping}, inplace=True)
                                st.write(f"Column {column_index}: '{selected_column}' has been mapped to '{chosen_mapping}'.")
                        else:
                            st.write("No changes have been made to the column.")

        st.session_state.df = df  # Save the DataFrame to session state for use in Page 2
