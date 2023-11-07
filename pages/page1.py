import streamlit as st
import pandas as pd
import fuzzywuzzy.process as fuzz
import re
import yaml

def page_1():
    # Access data from st.session_state
    df = st.session_state.df
    reference_columns = st.session_state.reference_columns

    st.title("Page 1: Automated and Manual Column Mapping")

    # Check if "Last Name" doesn't exist and create it
    if "Last Name" not in df.columns:
        df["Last Name"] = ""

    # Function to find and match columns
    def match_columns(df, reference_columns):
        matched_columns = {}  # Initialize the matched_columns dictionary

        input_columns = df.columns.tolist()

        for column in input_columns:
            matches = fuzz.extractBests(column, reference_columns)
            if matches:
                matched_columns[column] = matches

        return matched_columns

    # Automated column mapping
    matched_columns = match_columns(df, reference_columns)

    # Display initial mapping
    st.subheader("Mapped Columns:")
    for column, mapping in matched_columns.items():
        st.write(f"'{column}' is initially mapped to '{mapping[0][0]}'")

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
