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

# Page 1: Automated and Manual Column Mapping
def page_1():
    st.write("This is Page 1: Automated and Manual Column Mapping")

    # Access data from st.session_state
    df = st.session_state.df
    reference_columns = st.session_state.reference_columns
    
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

    st.subheader('Updated DataFrame:')
    st.write(df)

