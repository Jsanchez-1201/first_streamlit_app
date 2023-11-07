import streamlit as st
import pandas as pd
import fuzzywuzzy.process as fuzz
import re

def page_1():
    st.title("Page 1: Automated and Manual Column Mapping")

    # Access data from st.session_state
    df = st.session_state.df
    reference_columns = st.session_state.reference_columns
    default_yaml = st.session_state.default_yaml

    if default_yaml:
        st.write("Using the default YAML.")
    else:
        st.write("Using the uploaded YAML.")
    st.write("Your DataFrame:")
    st.write(df)

    if df is not None:
        last_name_pattern = re.compile(r'\b[lL][aA][sS][tT]\s?[nN][aA][mM][eE]\b|\bLST\s?NM\b')

        # Function to find and match columns
        def match_columns(df, reference_columns):
            matched_columns = {}  # Initialize the matched_columns dictionary

            input_columns = df.columns.tolist()

            for column in input_columns:
                matches = fuzz.extractBests(column, reference_columns)
                if matches:
                    matched_columns[column] = matches

            return matched_columns

        if default_yaml:
            # Load your default YAML here if needed
            reference_columns = []  # Replace with your default YAML

        # Automated column mapping
        matched_columns = match_columns(df, reference_columns)

        # Display initial mapping
        st.subheader("Mapped Columns:")
        for column, mapping in matched_columns.items():
            st.write(f"'{column}' is initially mapped to '{mapping[0][0]}'")

        # Manual column modification - you can implement your logic here

        # Check if "Last Name" doesn't exist and create it
        if "Last Name" not in df.columns:
            df["Last Name"] = ""

        # Allow the user to specify columns for modification
        st.subheader("Column Modification")
        change_columns_input = st.text_input("Enter a list of columns to modify (e.g., '0, 1, 2') or 'none' to skip:")
        if change_columns_input.lower() != 'none':
            # Implement your manual column mapping logic here

        # Remove columns that are not in reference_columns in the updated DataFrame
        columns_to_remove = [col for col in df.columns if col not in reference_columns]
        df.drop(columns=columns_to_remove, inplace=True)

        # Display the updated DataFrame
        st.subheader("Updated DataFrame:")
        st.write(df)
