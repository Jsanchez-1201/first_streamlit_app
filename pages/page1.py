import streamlit as st
import pandas as pd
import fuzzywuzzy.process as fuzz
import re
import yaml

def page_1():
    st.title("Page 1: Automated and Manual Column Mapping")

    # Access data from st.session_state or initialize if not exists
    if 'df' not in st.session_state:
        st.session_state.df = None

    if 'reference_columns' not in st.session_state:
        st.session_state.reference_columns = []

    if 'mapped_columns' not in st.session_state:
        st.session_state.mapped_columns = {}

    if 'process_change_columns' not in st.session_state:
        st.session_state.process_change_columns = False

    if 'change_columns_list' not in st.session_state:
        st.session_state.change_columns_list = []

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

    if st.session_state.df is not None:
        if not st.session_state.mapped_columns:
            # Perform initial automated mapping only once
            matched_columns = match_columns(st.session_state.df, st.session_state.reference_columns)
            st.session_state.mapped_columns = matched_columns

        # Display the mapped columns
        st.subheader('Mapped Columns:')
        mapped_columns_text = ""
        for column_index, (column, mapping) in enumerate(st.session_state.mapped_columns.items()):
            mapped_columns_text += f"{column_index}. '{column}' is initially mapped to '{mapping[0][0]}'\n"
        st.text(mapped_columns_text)

        # Use st.form for user input
        with st.form(key='user_input_form'):
            st.subheader('Column Modification')
            change_columns_input = st.text_input("Enter a list of columns to modify (e.g., '0, 5, 7') or 'none' to skip:", key="change_columns_input")
            submit_button = st.form_submit_button("Submit")

        # Process form submission
        if submit_button:
            if change_columns_input.lower() != 'none':
                change_columns_list = [int(col.strip()) for col in change_columns_input.split(',') if col.strip()]
                st.session_state.change_columns_list = change_columns_list
                st.session_state.process_change_columns = True
            else:
                st.session_state.process_change_columns = False

        # Process user input
        if st.session_state.process_change_columns:
            change_columns_list = st.session_state.change_columns_list
            matched_columns = st.session_state.mapped_columns

            for column_index in change_columns_list:
                if 0 <= column_index and column_index < len(matched_columns):
                    selected_column = list(matched_columns.keys())[column_index]
                    st.write(f"Mapping options for column {column_index}: '{selected_column}':")
                    for j, (match, score) in enumerate(matched_columns[selected_column]):
                        st.write(f"  {j}. Map to '{match}' (Score: {score})")
                    match_choice = st.text_input("Enter the number for the mapping, or 'skip' to keep as is:", key=f"match_choice_{column_index}")
                    if match_choice.lower() != 'skip' and match_choice.isdigit():
                        match_index = int(match_choice)
                        if 0 <= match_index < len(matched_columns[selected_column]):
                            chosen_mapping = matched_columns[selected_column][match_index][0]
                            # Rename columns one by one
                            st.session_state.df.rename(columns={selected_column: chosen_mapping}, inplace=True)
                            st.write(f"Column {column_index}: '{selected_column}' has been mapped to '{chosen_mapping}'.")
                        else:
                            st.write("No changes have been made to the columns.")
                    else:
                        st.write("Invalid input. Please enter a valid number or 'skip'.")

        # Remove columns that are not in reference_columns in the updated DataFrame
        columns_to_remove = [col for col in st.session_state.df.columns if col not in st.session_state.reference_columns and col not in st.session_state.mapped_columns]
        for col in columns_to_remove:
            st.session_state.df.drop(columns=col, inplace=True)

        # Add the "Last Name" column if it doesn't exist
        if "Last Name" not in st.session_state.df.columns:
            st.session_state.df["Last Name"] = ""

        # Display the updated DataFrame
        st.subheader('Updated DataFrame:')
        # Convert list-like objects to strings before displaying
        st.write(st.session_state.df.applymap(lambda x: ', '.join(x) if isinstance(x, list) else x))

if __name__ == "__main__":
    page_1()
