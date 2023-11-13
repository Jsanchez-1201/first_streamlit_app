import streamlit as st
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
import Levenshtein
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")

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
        clusters[label].append(data[header_name].iloc[i])
        old_names[label].append(data[header_name].iloc[i])

    st.session_state.clusters = clusters
    st.session_state.old_names = old_names

def move_cluster(item_to_move, from_cluster_id, to_cluster_id):
    editing_clusters = st.session_state.editing_clusters

    if item_to_move in editing_clusters[from_cluster_id]:
        editing_clusters[from_cluster_id].remove(item_to_move)
        editing_clusters[to_cluster_id].append(item_to_move)

    st.session_state.editing_clusters = editing_clusters

def merge_clusters(cluster1_id, cluster2_id):
    editing_clusters = st.session_state.editing_clusters

    editing_clusters[cluster1_id] += editing_clusters[cluster2_id]
    del editing_clusters[cluster2_id]

    st.session_state.editing_clusters = editing_clusters

def split_cluster(cluster_id, item_to_split):
    editing_clusters = st.session_state.editing_clusters

    if item_to_split in editing_clusters[cluster_id]:
        editing_clusters[cluster_id].remove(item_to_split)
        new_cluster_id = max(editing_clusters.keys()) + 1
        editing_clusters[new_cluster_id] = [item_to_split]

    st.session_state.editing_clusters = editing_clusters

def create_cluster(new_item):
    editing_clusters = st.session_state.editing_clusters
    
    new_cluster_id = max(clusters.keys()) + 1
    editing_clusters[new_cluster_id] = [new_item]

    st.session_state.editing_clusters = editing_clusters

def replace_cluster(edit_cluster, name_to_edit):
    editing_clusters = st.session_state.editing_clusters

    for item in editing_clusters[edit_cluster]:
        if item != name_to_edit:
          editing_clusters[edit_cluster][editing_clusters[edit_cluster].index(item)] = name_to_edit
    
    st.session_state.editing_clusters = editing_clusters

def editing_cluster(data, header_name):
    editing_clusters = st.session_state.editing_clusters

    while True:
        st.write("Current Clusters:")
        for cluster_label, cluster_items in editing_clusters.items():
            st.write(f"Cluster {cluster_label}: {cluster_items}")

        choice = st.selectbox("Options for editing clusters:", ("Move an item to another cluster", "Merge clusters", "Split a cluster", 
                                                                "Create a new cluster", "Edit the information within the cluster", "Skip"))

        # choice should be a list?
        # so in the if statement i can use the indexes

        if choice == "Move an item to another cluster":
            item_to_move = st.text_input("Enter the item you want to move:", key="item_to_move_input")
            from_cluster_id = st.text_input("Enter the current cluster ID:", key="from_cluster_id_input")
            to_cluster_id = st.text_input("Enter the target cluster ID:", key="to_cluster_id_input")
            submit_button = st.button("Move item")

            if submit_button:
                st.session_state.item_to_move = item_to_move
                st.session_state.from_cluster_id = from_cluster_id
                st.session_state.to_cluster_id = to_cluster_id
                move_cluster(item_to_move, from_cluster_id, to_cluster_id)

        elif choice == "Merge clusters":
            cluster1_id = st.text_input("Enter the first cluster ID to merge:", key="cluster1_input")
            cluster2_id = st.text_input("Enter the second cluster ID to merge:", key="cluster2_input")
            submit_button = st.button("Merge clusters")

            if submit_button:
                st.session_state.cluster1_id = cluster1_id
                st.session_state.cluster2_id = cluster2_id
                merge_clusters(cluster1_id, cluster2_id)

        elif choice == "Split a cluster":
            cluster_id = st.text_input("Enter the cluster ID to split:", key="clusterID_input")
            item_to_split = st.text_input("Enter the item you want to split:", key="split_input")
            submit_button = st.button("Split cluster")

            if submit_button:
                st.session_state.cluster_id = cluster_id
                st.session_state.item_to_split = item_to_split
                split_cluster(cluster_id, item_to_split)
        
        elif choice == "Create a new cluster":
            new_item = st.text_input("Enter the new item to create a cluster:", key="new_item_input")
            submit_button = st.button("Create new cluster")

            if submit_button:
                st.session_state.new_item = new_item
                create_cluster(new_item)
        
        elif choice == "Edit the information within the cluster":
            edit_cluster = st.text_input("Enter the cluster ID to edit:", key="edit_cluster_input")
            name_to_edit = st.text_input("Enter the name you want to replace:", key="edit_name_input")
            submit_button = st.button("Edit cluster")

            if submit_button:
                st.session_state.edit_cluster = edit_cluster
                st.session_state.name_to_edit = name_to_edit
                replace_cluster(edit_cluster, name_to_edit)
        
        elif choice == "Skip":
            break
    
    data[header_name] = data[header_name].str.lower()
    for clusters_key, clusters_items in old_names.items():          
          for item in clusters_items:
            data = data.replace(item, editing_clusters[clusters_key][0])
    
    return editing_clusters # this return could retrieves an error

def page_2():
    st.title("Cluster Functions")
    
    updated_dataframe = None
    editing_clusters = None
    if 'df' in st.session_state:
        updated_dataframe = st.session_state.df
        st.write("Updated dataframe:")
        st.write(updated_dataframe)
    if 'header_name' not in st.session_state:
        st.session_state.header_name = 'none'
    if 'distance_matrix' not in st.session_state:
        st.session_state.distance_matrix = None
    if 'clusters' not in st.session_state:
        st.session_state.clusters = [] # changed None to []
    if 'old_names' not in st.session_state:
        st.session_state.old_names = None
    if 'item_to_move' not in st.session_state:
        st.session_state.item_to_move = 'none'
    if 'from_cluster_id' not in st.session_state:
        st.session_state.from_cluster_id = 'none'
    if 'to_cluster_id' not in st.session_state:
        st.session_state.from_cluster_id = 'none'
    if 'editing_clusters' not in st.session_state:
        st.session_state.editing_clusters = None
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

    if updated_dataframe is not None:
        header_name = st.text_input("Enter the Header Name:", key="header_name_input")
        submit_button = st.button("Compute Clustering")

        if submit_button:
            st.session_state.header_name = header_name
            perform_clustering(updated_dataframe, header_name)

            # # Display the computed distance matrix
            # st.subheader('Distance Matrix:')
            # if st.session_state.distance_matrix is not None:
            #     st.write(st.session_state.distance_matrix)

            # Display the clustering results
            st.subheader('Clustering Results:')
            if st.session_state.clusters is not None:
                st.write(st.session_state.clusters)

            editing_clusters = editing_cluster(updated_dataframe, header_name) # took out the arg: updated_dataframe
            st.session_state.editing_clusters = editing_clusters # updating editing_clusters 

    return st.session_state.clusters, st.session_state.old_names, st.session_state.header_name, st.session_state.editing_clusters

clusters, old_names, header_name, editing_clusters = page_2()