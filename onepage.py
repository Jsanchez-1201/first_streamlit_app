import streamlit as st
import pandas as pd
import numpy as np
import fuzzywuzzy.process as fuzz
import re
import sys
import yaml
from sklearn.cluster import DBSCAN
import Levenshtein
import warnings
from collections import defaultdict

# Page configuration
st.set_page_config(
    layout="centered"
)

# Initialize session states variables
if 'current_page_number' not in st.session_state:
    st.session_state.current_page_number = 0

# Inits placeholder container to add / delete as required
if 'current_page_container' not in st.session_state:
    st.session_state.current_page_container = st.empty()

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
if 'distance_matrix' not in st.session_state:
    st.session_state.distance_matrix = None
if 'clusters' not in st.session_state:
    st.session_state.clusters = {} # changed None to {}
if 'old_names' not in st.session_state:
    st.session_state.old_names = None
if 'item_to_move' not in st.session_state:
    st.session_state.item_to_move = 'none'
if 'from_cluster_id' not in st.session_state:
    st.session_state.from_cluster_id = 'none'
if 'to_cluster_id' not in st.session_state:
    st.session_state.from_cluster_id = 'none'
if 'cluster1_id' not in st.session_state:
    st.session_state.cluster1_id = 'none'
if 'cluster2_id' not in st.session_state:
    st.session_state.cluster2_id = 'none'
if 'cluster_id' not in st.session_state:
    st.session_state.cluster_id = 'none'
if 'item_to_split' not in st.session_state:
    st.session_state.item_to_split = 'none'
if 'new_item' not in st.session_state:
    st.session_state.new_item = 'none'
if 'edit_cluster' not in st.session_state:
    st.session_state.edit_cluster = 'none'
if 'name_to_edit' not in st.session_state:
    st.session_state.name_to_edit = 'none'
if 'header_name' not in st.session_state:
    st.session_state.header_name = 'none' # take a look
if "Move Item" not in st.session_state:
    st.session_state["Move Item"] = False
if 'Move' not in st.session_state:
    st.session_state["Move"] = False
if "Create Cluster" not in st.session_state:
    st.session_state["Create Cluster"] = False
if 'Create' not in st.session_state:
    st.session_state["Create"] = False
if "Split Cluster" not in st.session_state:
    st.session_state["Split Cluster"] = False
if 'Split' not in st.session_state:
    st.session_state["Split"] = False
if "Merge Cluster" not in st.session_state:
    st.session_state["Merge Cluster"] = False
if 'Merge' not in st.session_state:
    st.session_state["Merge"] = False
if "Edit Cluster" not in st.session_state:
    st.session_state["Edit Cluster"] = False
if 'Edit Information' not in st.session_state:
    st.session_state["Edit Information"] = False
if "Save Changes" not in st.session_state:
    st.session_state["Save Changes"] = False
if "Create column(s)" not in st.session_state:
    st.session_state["Create column(s)"] = False
if 'column_to_split' not in st.session_state:
    st.session_state.column_to_split = 'none'
if 'character' not in st.session_state:
    st.session_state.character = 'none'
if 'column_names' not in st.session_state:
    st.session_state.column_names = 'none'
if "Split into Columns" not in st.session_state:
    st.session_state["Split into Columns"] = False # submit button

st.write(st.session_state.current_page_number)

#Next page
def step_up():
    st.session_state.current_page_number = st.session_state.current_page_number + 1

#Back page
def step_down():
    if not st.session_state.current_page_number <= 0:
        st.session_state.current_page_number = st.session_state.current_page_number - 1

def match_columns(df, reference_columns):
    matched_columns = {}
    input_columns = df.columns.tolist()
    for column in input_columns:
        matches = fuzz.extract(column, reference_columns)
        if matches:
            matched_columns[column] = matches
    return matched_columns

def perform_initial_mapping():
    matched_columns = match_columns(st.session_state.df, st.session_state.reference_columns)
    st.session_state.mapped_columns = matched_columns
    # unique_identifier = 1
    for column, mapping in matched_columns.items():
        new_column_name = mapping[0][0]
        while new_column_name in st.session_state.df.columns:
            new_column_name = f"{mapping[0][0]}" # _{unique_identifier}
            # unique_identifier += 1
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
                                            key="change_columns_input") # value=st.session_state.change_columns_input
        submit_button = st.form_submit_button("Submit")
    
    if submit_button:
        st.session_state.form_submitted = True
        # st.session_state.change_columns_input = change_columns_input
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

                        # Check if the chosen mapping already exists as a column
                        if chosen_mapping in st.session_state.df.columns:
                            st.write(f"Column name '{chosen_mapping}' already exists. Please choose a different name.")
                        else:
                            st.session_state.df.rename(columns={selected_column: chosen_mapping}, inplace=True)
                            st.write(f"Column {column_index}: '{selected_column}' has been mapped to '{chosen_mapping}'.")
                    else:
                        st.write("Invalid input. Please enter a valid number or 'skip'.")
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
    return updated_df

# Apply automatic functions
def job_title(df):
    try:
        # df.Title.fillna('', inplace=True)
        mask = df['Title'].apply(lambda x: len(str(x)) != 0)
        df['Title_validation'] = ''
        df['Title_validation'][mask == True] = 'Valid'
        df['Title_validation'][mask == False] = 'Invalid'
        return df
    except:
        st.write("Please ensure that the designated column is labeled 'Title'. Kindly select the appropriate option prior to rerunning the process.")
    
def split_name(df):
    try:
        if df['Last Name'].isnull().values.any() == False:
            df["First Name"] = df["First Name"].replace('[-| .,\/_]+',' ', regex = True)
            new = df["First Name"].str.split(" ", n=1, expand = True)
            df["First Name"] = new[0]
            df["Last Name"] = new[1]
            return df
        else:
            st.write("This database already has both Name and Last Name in different columns.")
    except:
        st.write("Please ensure that the designated column is labeled 'First Name'. Kindly select the appropriate option prior to rerunning the process.")

def validate_names(data):
    try:
        lenght = data['First Name'].str.len()
        mask = lenght >= 2
        data['Name_validation'] = ''
        data['Name_validation'][mask == True] = 'Valid'
        data['Name_validation'][mask == False] = 'Invalid'
        return data
    except:
        st.write("Please ensure that the designated column is labeled 'First Name'. Kindly select the appropriate option prior to rerunning the process.")
    
def validate_emails(df):

    # Extracting the Email and Lead Gatherer Email columns
    email_columns = ['Email']
    # Initialize valid email pattern
    pattern = '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}'
    # Iterate through the specified columns
    for column in email_columns:
        column_name = f'{column} Validation'
        is_valid_pattern = df[column_name] = df[column].apply(lambda email: bool(re.match(pattern, email)))
        invalid_domains = ['gmail.com', 'hotmail.com']
        invalid_domains = ['gmail.com', 'hotmail.com']
        is_valid_domain = ~df[column].str.lower().str.endswith(tuple(invalid_domains))
        df[column_name] = np.where(is_valid_pattern & is_valid_domain, 'Valid', 'Invalid')
    # Display the modified DataFrame
    return df


def map_work_columns(data):
    data.columns = data.columns.str.replace('Work ', '')
    return data

def clean_none(df):
    df.fillna('', inplace=True)
    return df

df = st.session_state.df
reference_columns = st.session_state.reference_columns

# Functions related to clustering

def levenshtein_distance(s1, s2):
    return Levenshtein.distance(s1, s2)

def compute_distance_matrix(data, header_name):
    texts = data[header_name].str.lower()
    distance_matrix = np.zeros((len(texts), len(texts)))
    for i in range(len(texts)):
        for j in range(i, len(texts)):
            distance_matrix[i, j] = levenshtein_distance(texts[i], texts[j])
            distance_matrix[j, i] = distance_matrix[i, j]
    return distance_matrix

def perform_clustering(data, header_name):
    distance_matrix = compute_distance_matrix(data, header_name)
    st.session_state.distance_matrix = distance_matrix
    
    dbscan = DBSCAN(eps=0.05, min_samples=1, metric="cosine")
    labels = dbscan.fit_predict(distance_matrix)

    clusters = defaultdict(list)
    old_names = defaultdict(list)
    for i, label in enumerate(labels):
        label_key = int(label) # convert numpy.int64 to int
        clusters[label_key].append(data[header_name].iloc[i])
        old_names[label_key].append(data[header_name].iloc[i])

    clusters = dict((k, [x.lower() for x in v]) for k,v in clusters.items())
    old_names = dict((k, [x.lower() for x in v]) for k,v in clusters.items())
    st.session_state.clusters = clusters
    st.session_state.old_names = old_names
    # st.write(clusters)
    return st.session_state.clusters, st.session_state.old_names

def move_cluster(item_to_move, from_cluster_id, to_cluster_id):
    
    clusters = st.session_state.clusters

    if item_to_move in clusters[int(from_cluster_id)]:
        clusters[int(to_cluster_id)].append(item_to_move)
        clusters[int(from_cluster_id)].remove(item_to_move)

    st.session_state.clusters = clusters

    for cluster_label, cluster_items in clusters.items():
        st.write(f"Cluster {cluster_label}: {cluster_items}")

def merge_clusters(cluster1_id, cluster2_id):
    
    clusters = st.session_state.clusters

    clusters[int(cluster1_id)] += clusters[int(cluster2_id)]
    del clusters[int(cluster2_id)]

    st.session_state.clusters = clusters

    for cluster_label, cluster_items in clusters.items():
        st.write(f"Cluster {cluster_label}: {cluster_items}")

def split_cluster(cluster_id, item_to_split):
    
    clusters = st.session_state.clusters

    if item_to_split in clusters[int(cluster_id)]:
        clusters[int(cluster_id)].remove(item_to_split)
        new_cluster_id = max(clusters.keys()) + 1
        clusters[new_cluster_id] = [item_to_split]

    st.session_state.clusters = clusters

    for cluster_label, cluster_items in clusters.items():
        st.write(f"Cluster {cluster_label}: {cluster_items}")

def create_cluster(new_item):
    
    clusters = st.session_state.clusters
    
    new_cluster_id = max(clusters.keys()) + 1
    clusters[new_cluster_id] = [new_item]

    st.session_state.clusters = clusters

    for cluster_label, cluster_items in clusters.items():
        st.write(f"Cluster {cluster_label}: {cluster_items}")

def replace_cluster(edit_cluster, name_to_edit):
    
    clusters = st.session_state.clusters

    for item in clusters[int(edit_cluster)]:
        if item != name_to_edit:
          clusters[int(edit_cluster)][clusters[int(edit_cluster)].index(item)] = name_to_edit
    
    st.session_state.clusters = clusters

    for cluster_label, cluster_items in clusters.items():
        st.write(f"Cluster {cluster_label}: {cluster_items}")

def editing_cluster(clusters, old_names, data, header_name):
    
    clusters = st.session_state.clusters
    old_names = st.session_state.old_names

    col1 = "Move Item"
    col2 = "Create Cluster"
    col3 = "Split Cluster"
    col4 = "Merge Cluster"
    col5 = "Edit Cluster"
    col6 = "Save Changes"

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    
    with col1:
        if st.button("Move Item"):
            st.session_state["Move Item"] = not st.session_state["Move Item"]

        if st.session_state["Move Item"]:
            # Pressed first button
            with st.form(key='move_input_form'):
                st.subheader('Move Item Modification')
                item_to_move = st.text_input("Enter the item you want to move:", key="item_to_move_input")
                from_cluster_id = st.text_input("Enter the current cluster ID:", key="from_cluster_id_input")
                to_cluster_id = st.text_input("Enter the target cluster ID:", key="to_cluster_id_input")
                submit_button = st.form_submit_button("Move")
                if submit_button:
                    st.session_state.form_submitted = True
                    st.session_state.item_to_move = item_to_move
                    st.session_state.from_cluster_id = from_cluster_id
                    st.session_state.to_cluster_id = to_cluster_id
                    move_cluster(item_to_move, from_cluster_id, to_cluster_id) 
            
            st.session_state["Move"] = not st.session_state["Move"]

    with col2:   
        if st.button("Create Cluster"):
            st.session_state["Create Cluster"] = not st.session_state["Create Cluster"]

        if st.session_state["Create Cluster"]:
            with st.form(key='create_input_form'):
                st.subheader('Create Cluster')
                new_item = st.text_input("Enter the new item to create a cluster:", key="new_item_input")
                submit_button = st.form_submit_button("Create")

                if submit_button:
                    st.session_state.form_submitted = True
                    st.session_state.new_item = new_item
                    create_cluster(new_item)
            
            st.session_state["Create"] = not st.session_state["Create"]

    with col3:    
        if st.button("Split Cluster"):
            st.session_state["Split Cluster"] = not st.session_state["Split Cluster"]

        if st.session_state["Split Cluster"]:
            with st.form(key='split_input_form'):
                st.subheader('Split Cluster')
                cluster_id = st.text_input("Enter the cluster ID to split:", key="clusterID_input")
                item_to_split = st.text_input("Enter the item you want to split:", key="split_input")
                submit_button = st.form_submit_button("Split")

                if submit_button:
                    st.session_state.form_submitted = True
                    st.session_state.cluster_id = cluster_id
                    st.session_state.item_to_split = item_to_split
                    split_cluster(cluster_id, item_to_split)
            
            st.session_state["Split"] = not st.session_state["Split"]

    with col4:
        if st.button("Merge Cluster"):
            st.session_state["Merge Cluster"] = not st.session_state["Merge Cluster"]

        if st.session_state["Merge Cluster"]:
            with st.form(key='merge_input_form'):
                st.subheader('Merge Cluster')
                cluster1_id = st.text_input("Enter the first cluster ID to merge:", key="cluster1_input")
                cluster2_id = st.text_input("Enter the second cluster ID to merge:", key="cluster2_input")
                submit_button = st.form_submit_button("Merge")

                if submit_button:
                    st.session_state.form_submitted = True
                    st.session_state.cluster1_id = cluster1_id
                    st.session_state.cluster2_id = cluster2_id
                    merge_clusters(cluster1_id, cluster2_id)
            
            st.session_state["Merge"] = not st.session_state["Merge"]
    
    with col5:
        if st.button("Edit Cluster"):
            st.session_state["Edit Cluster"] = not st.session_state["Edit Cluster"]

        if st.session_state["Edit Cluster"]:
            with st.form(key='edit_input_form'):
                st.subheader('Edit Information')
                edit_cluster = st.text_input("Enter the cluster ID to edit:", key="edit_cluster_input")
                name_to_edit = st.text_input("Enter the name you want to replace:", key="edit_name_input")
                submit_button = st.form_submit_button("Edit Information")
                
                if submit_button:
                    st.session_state.form_submitted = True
                    st.session_state.edit_cluster = edit_cluster
                    st.session_state.name_to_edit = name_to_edit
                    replace_cluster(edit_cluster, name_to_edit)
            
            st.session_state["Edit Information"] = not st.session_state["Edit Information"]
    
    with col6:
        if st.button("Save Changes"):
            st.session_state["Save Changes"] = not st.session_state["Save Changes"]

        if st.session_state["Save Changes"]:
            # st.write(clusters)
            # st.write(old_names)
            data[header_name] = data[header_name].str.lower()
            for clusters_key, clusters_items in old_names.items():        
                for item in clusters_items:
                    data = data.replace(item, clusters[clusters_key][0]) # remove int
            
            st.session_state.df = data
            st.write(data)

    return st.session_state.df

def splitting(df, column_to_split, character):
    
    if column_to_split not in df.columns:
        st.write("Column not found")

    else:
        splits = df[column_to_split].tolist()
        size = 0
        for name in splits:
            names = name.split(character)
            if len(names) > size:
                size = len(names)
        st.write(f'You have to enter {size} name(s) for the new column(s)')
        
        if st.button("Create column(s)"):
            st.session_state["Create column(s)"] = not st.session_state["Create column(s)"]
        
        if st.session_state["Create column(s)"]:
        # Create columns button
            with st.form(key='split_form'):
                df_column = []
                for i in range(size):
                    column_names = st.text_input("Select the new column name:", key=f'asljalsjdlksajdklajsldkjaslkdj{str(i)}')
                    df_column.append(column_names)     
                
                submit_button = st.form_submit_button("Split into Columns")
                
                if submit_button:
                    st.session_state.form_submitted = True
                    st.session_state.column_names = column_names
                    
                    df[df_column] = df[column_to_split].str.split(character, expand=True)
            
            st.session_state["Split into Columns"] = not st.session_state["Split into Columns"]
        
        st.write(st.session_state.df)
    
    return st.session_state.df

def search_replace(df):
    if 'df' not in st.session_state:
        st.error("DataFrame not found in session state. Please upload or create a DataFrame in the previous steps.")
        return

    if 'choice' not in st.session_state:
        st.session_state.choice = None

    if 'column_name' not in st.session_state:
        st.session_state.column_name = None

    if 'find_value' not in st.session_state:
        st.session_state.find_value = None

    if 'replace_value' not in st.session_state:
        st.session_state.replace_value = None

    if 'preview_dataframe' not in st.session_state:
        st.session_state.preview_dataframe = st.session_state.df
    
    st.subheader("Preview DataFrame:")
    st.write(st.session_state.preview_dataframe)
  
    st.session_state.choice = st.radio("Select the level you want to change the value from, Finish to end the process", ['Specific Column', 'Whole DataFrame', 'Finish'], key='level_radio1')

    if st.session_state.choice == 'Specific Column':
        st.session_state.column_name = st.text_input("Enter the column name in which to replace the value (or 'Finish' to exit):", key='Columnas')
        if st.session_state.column_name and st.session_state.column_name.lower() != 'finish' and st.session_state.column_name in st.session_state.df.columns:
            with st.form(key='specific_column_form'):
                st.session_state.find_value = st.text_input("Enter the value to find:", key='find_value_col')
                st.session_state.replace_value = st.text_input("Enter the value to replace it with:", key='replace_value_col')
                submitted = st.form_submit_button('Replace')

                if submitted:
                    # Check if the find_value exists in the specified column
                    if st.session_state.find_value not in st.session_state.df[st.session_state.column_name].values:
                        st.error(f"Value '{st.session_state.find_value}' not found in column '{st.session_state.column_name}'. Please enter a valid value.")
                    else:
                        st.session_state.df[st.session_state.column_name].replace(st.session_state.find_value, st.session_state.replace_value, inplace=True)
                        st.write(f"Value replaced in {st.session_state.column_name}")
        elif st.session_state.column_name not in st.session_state.df.columns or st.session_state.column_name in [' ', '']:
            st.warning(f"Column '{st.session_state.column_name}' not found in DataFrame. Please enter a valid column name.")
    elif st.session_state.choice == 'Whole DataFrame':
        with st.form(key='whole_dataframe_form'):
            st.session_state.find_value = st.text_input("Enter the value to find:", key='find_value_df')
            st.session_state.replace_value = st.text_input("Enter the value to replace it with:", key='replace_value_df')
            submitted_whole = st.form_submit_button('Replace')

            if submitted_whole:
                # Check if the find_value exists in the entire DataFrame
                if st.session_state.find_value not in st.session_state.df.values:
                    st.error(f"Value '{st.session_state.find_value}' not found in the DataFrame. Please enter a valid value.")
                else:
                    st.session_state.df.replace(st.session_state.find_value, st.session_state.replace_value, inplace=True)
                    st.write("Values replaced in the whole DataFrame")
    elif st.session_state.choice == 'Finish':
        st.success('Replace process finished')

    st.subheader("DataFrame after replacement:")
    st.write(st.session_state.df)

def render_page_main():
    # Your page code here
    st.title("Automated and Manual Cleaning")
    uploaded_file = st.file_uploader("Upload Excel or CSV File", type=["xlsx", "csv"], key="file_uploader")
    reference_file = st.file_uploader("Upload YAML file with reference columns (optional)", type=["yml", "yaml"], key="yaml_uploader")

    with open('standard_columns.yml', 'r') as default_yaml:
        default_reference_columns = yaml.safe_load(default_yaml)
    
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        if file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file) # Read Excel file
        elif file_extension == 'csv':
            df = pd.read_csv(uploaded_file) # Read CSV file
        else:
            st.error(f"Unsupported file type: {file_extension}. Please upload an Excel (xlsx/xls) or CSV file.")

    if reference_file is not None:
        with reference_file as file:
            try:
                st.session_state.reference_columns = yaml.safe_load(file) # fix the error with the variable
            except Exception as e:
                st.error(f"Error loading reference columns: {str(e)}")
        st.session_state.df = df

    
    if st.button("Continue with Default YAML"):
        st.session_state.df = df
        st.session_state.reference_columns = default_reference_columns
    st.subheader("Data preview:")
    st.write(st.session_state.df)

st.session_state.df = df
st.session_state.reference_columns = reference_columns

def render_first_page():
    st.title("Automated and Manual Cleaning")

    if st.session_state.df is not None:
        if not st.session_state.mapped_columns:
            perform_initial_mapping()

        display_mapped_columns()
        process_user_input()

    process_user_input_changes()
    data = update_dataframe()

    if st.button("Apply automatic functions"):
        if st.session_state.df is not None:
            clean_none(data)
            job_title(data)
            split_name(data)
            validate_names(data)
            validate_emails(data)
            map_work_columns(data)
        st.subheader("Updated data:")
        st.write(st.session_state.df)
    return st.session_state.df

def render_second_page():

    st.title("Clustering Function")
    st.write("This function is designed to group related data, allowing users to effortlessly make typo corrections without requiring a specific input.")
    if st.session_state.df is not None:
        column_names = []
        for i in range(len(st.session_state.df.columns)):
            column_names.append(st.session_state.df.columns[i])
        st.write("Here there is a list of valid Header Names:")
        st.write(f"{column_names}")
        # st.write(st.session_state.df.columns) # fix the UI
        header_name = st.text_input("Enter the Column Name:", key="header_name_input")
        if not header_name:
            pass
        elif header_name in st.session_state.df.columns:
            submit_button = st.button("Compute Clustering")

            if submit_button:
                st.session_state.header_name = header_name
                clusters, old_names = perform_clustering(st.session_state.df, header_name)

            clusters = st.session_state.clusters
            old_names = st.session_state.old_names

            # Display the clustering results
            st.write("Current Clusters:")
            for cluster_label, cluster_items in clusters.items():
                st.write(f"Cluster {cluster_label}: {cluster_items}")
    
            clean_data = editing_cluster(clusters, old_names, st.session_state.df, header_name)
            st.session_state.df = clean_data
        
        else:
            st.write("Please provide a valid Column Name")
            
    return st.session_state.df # idk if it makes sense

def render_third_page():
    
    st.title("Splitting Columns")
    st.write("This function facilitates the division of particular columns according to their content. The application will prompt you to assign new names to the resulting columns based on the extracted words.")
    if st.session_state.df is not None:
        column_to_split = st.text_input("Select the column you want to split:", key="column_to_split_input")
        character = st.text_input("Select the character you want to split by:", key="character_input")
        
        if not character:
            pass
        else:
            splitting(st.session_state.df, column_to_split, character)
    
def render_fourth_page():
    st.title("Find and Replace Function")

    if st.session_state.df is not None:
        search_replace(st.session_state.df)

#Based on page number render required contents
def render_page(page_number):

    #Idk why but without rendering something first, it wont work
    st.write(' ')
    with st.session_state.current_page_container.container():

        #First page, call function that has UI comps
        if page_number == 0:
            render_page_main() # load files
        elif page_number == 1:
            render_first_page() # mapping and automatic functions
        elif page_number == 2:
            render_second_page() # clustering functions
        elif page_number == 3:
            render_third_page() # Splitting columns
        elif page_number == 4:
            render_fourth_page() # Find and Replace Function

render_page(st.session_state.current_page_number)
        
#Navigation buttons
col1, mid, col2 = st.columns([1,3,1])

#Display back button only if not on first page
if st.session_state.current_page_number != 0:
    with col1:
        back = st.button('Back', on_click = step_down, type = 'primary', use_container_width=True)

#Change based on amount of pages/steps
pages = 5
if st.session_state.current_page_number != pages - 1 :
    with col2:
        next = st.button('Next', on_click = step_up, type = 'primary', use_container_width=True)
