import streamlit as st
import pandas as pd
import fuzzywuzzy.process as fuzz
import sys
import re
import yaml

def initialize_session_state():
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
    if 'change_columns_input' not in st.session_state:
        st.session_state.change_columns_input = ''
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False

def match_columns(df, reference_columns):
    matched_columns = {}
    input_columns = df.columns.tolist()
    for column in input_columns:
        matches = fuzz.extractBests(column, reference_columns)
        if matches:
            matched_columns[column] = matches
    return matched_columns

def perform_initial_mapping():
    matched_columns = match_columns(st.session_state.df, st.session_state.reference_columns)
    st.session_state.mapped_columns = matched_columns
    unique_identifier = 1
    for column, mapping in matched_columns.items():
        new_column_name = mapping[0][0]
        while new_column_name in st.session_state.df.columns:
            new_column_name = f"{mapping[0][0]}_{unique_identifier}"
            unique_identifier += 1
        st.session_state.df.rename(columns={column: new_column_name}, inplace=True)

def display_mapped_columns():
    st.subheader('Mapped Columns:')
    mapped_columns_text = ""
    for column_index, (column, mapping) in enumerate(st.session_state.mapped_columns.items()):
        mapped_columns_text += f"{column_index}. '{column}' is initially mapped to '{mapping[0][0]}'\n"
    st.text(mapped_columns_text)

def process_user_input():
    with st.form(key='user_input_form'):
        st.subheader('Column Modification')
        change_columns_input = st.text_input("Enter a list of columns to modify (e.g., '0, 5, 7') or 'none' to skip:",
                                            key="change_columns_input", value=st.session_state.change_columns_input)
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        st.session_state.form_submitted = True
        st.session_state.change_columns_input = change_columns_input
        if change_columns_input.lower() != 'none':
            change_columns_list = [int(col.strip()) for col in change_columns_input.split(',') if col.strip()]
            st.session_state.change_columns_list = change_columns_list
            st.session_state.process_change_columns = True
        else:
            st.session_state.process_change_columns = False

def process_user_input_changes():
    if st.session_state.form_submitted and st.session_state.process_change_columns:
        change_columns_list = st.session_state.change_columns_list
        matched_columns = st.session_state.mapped_columns
        for column_index in change_columns_list:
            if 0 <= column_index < len(matched_columns):
                selected_column = list(matched_columns.keys())[column_index]
                st.write(f"Mapping options for column {column_index}: '{selected_column}':")
                for j, (match, score) in enumerate(matched_columns[selected_column]):
                    st.write(f"  {j}. Map to '{match}' (Score: {score})")
                match_choice = st.text_input("Enter the number for the mapping, or 'skip' to keep as is:",
                                             key=f"match_choice_{column_index}")
                if match_choice.lower() != 'skip' and match_choice.isdigit():
                    match_index = int(match_choice)
                    if 0 <= match_index < len(matched_columns[selected_column]):
                        chosen_mapping = matched_columns[selected_column][match_index][0]
                        st.session_state.df.rename(columns={selected_column: chosen_mapping}, inplace=True)
                        st.write(f"Column {column_index}: '{selected_column}' has been mapped to '{chosen_mapping}'.")
                    else:
                        st.write("No changes have been made to the columns.")
                else:
                    st.write("Invalid input. Please enter a valid number or 'skip'.")

def update_dataframe():
    if "Last Name" not in st.session_state.df.columns:
        st.session_state.df["Last Name"] = ""

    updated_df = st.session_state.df.copy()
    updated_df["Last Name"] = st.session_state.df["Last Name"]  # Modify the copy

    st.subheader('Updated DataFrame:')
    st.write(updated_df)

    st.session_state.df = updated_df

# Apply automatic functions
def job_title(df):
    st.session_state.df = updated_df
    try:
        missing_job = df['Title'].isna().sum()
        count = df['Title'].count() + missing_job
        percentage = (missing_job/count)
        if percentage <= 0.25:
            df = df[df['Title'].notna()]
            st.write ('All the records with missing information were deleted. Job Title has their 75% with valid information.')
        else:
            st.write('In this dataset, less than 75% does not have Job Title completed')
        return df
    except OSError as e:
            print(f"Unable to open {df} because: {e}", file=sys.stderr)
            return
    
def split_name(df):
    if df['Last Name'].isnull().values.any() == True:
        df = df.replace('[-| .,\/_]+',' ', regex = True)
        new = df["First Name"].str.split(" ", n=1, expand = True)
        df["First Name"] = new[0]
        df["Last Name"] = new[1]
    else:
        st.write("This database already has both Name and Last Name in different columns.")
    return df
    
def validate_names(data):
    data_temp = data
    data = data[data['First Name'].notna()]
    lenght = data['First Name'].str.len()
    mask = lenght >= 2
    data = data[mask]
    name_nulls = data_temp['First Name'].isna().sum()
    count_total_temp = data_temp['First Name'].count() + name_nulls
    count_rows = data['First Name'].count()
    percentage = count_rows/count_total_temp
    if percentage <= 0.25:
        st.write('All the records with missing information were deleted. Name has their 75% with information.')
    else:
        st.write('In this dataset, less than 75% does not have a valid Name')
    return data
    
def validate_emails(df):
    # Extracting the Email and Lead Gatherer Email columns
    email_columns = ['Email']
    # Initialize valid email pattern
    pattern = '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}'
    # Iterate through the specified columns
    for column in email_columns:
        column_name = f'{column} Validation'
        df[column_name] = df[column].apply(lambda email: bool(re.match(pattern, email)))
        df[column_name] = df[column_name].apply(lambda is_valid: 'Valid' if is_valid else 'Invalid')
    # Display the modified DataFrame
    return df

def map_work_columns(data):
    data.columns = data.columns.str.replace('Work ', '')
    return data

def page_1():
    st.title("Automated and Manual Cleaning")

    initialize_session_state()

    if st.session_state.df is not None:
        if not st.session_state.mapped_columns:
            perform_initial_mapping()

        display_mapped_columns()
        process_user_input()

    process_user_input_changes()
    update_dataframe()

    if st.button("Apply automatic functions"):
        if st.session_state.df is not None:
            job_title(df) # how to pass arguments
            split_name(df)
            validate_names(df)
            validate_emails(df)
            map_work_columns(data)

    return st.session_state.df

if __name__ == "__main__":
    page_1()