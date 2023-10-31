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

    with open('standard_columns.yml', 'r') as yaml_file:
        try:
            reference_columns = yaml.safe_load(yaml_file)
        except Exception as e:
            print(f"Error loading reference columns: {str(e)}")
            reference_columns = []

    if reference_columns:
        matched_columns = match_columns(df, reference_columns)

        # Initial automated mapping
        for index, (column, matches) in enumerate(matched_columns.items()):
            if len(matches) > 0:
                best_match = matches[0][0]  # Get the full matched column name
                df.rename(columns={column: best_match}, inplace=True)
                print(f"{index}. Column '{column}' mapped to '{best_match}'")

        print("Initial mapping finished.")

        # Remove columns that are not in reference_columns
        columns_to_remove = [col for col in df.columns if col not in reference_columns]
        df.drop(columns=columns_to_remove, inplace=True)

        # Check if "Last Name" doesn't exist and create it
        if "Last Name" not in df.columns:
            df["Last Name"] = ""

        # Allow the user to specify columns for modification
        execution = True
        while execution:
            change_columns_input = input("Enter a list of columns to modify (e.g., '0, 5, 7') or 'none' to skip: ")
            
            if change_columns_input.lower() != 'none':
                change_columns_list = [int(col.strip()) for col in change_columns_input.split(',')]

                for column_index in change_columns_list:
                    print(column_index, type(column_index), len(matched_columns))
                    if 0 <= column_index and column_index < len(matched_columns):
                        selected_column = list(matched_columns.keys())[column_index]
                        selected_columntemp = df.columns.tolist()[column_index]
                        print(f"Mapping options for column {column_index}: '{selected_column}':")
                        for j, (match, score) in enumerate(matched_columns[selected_column]):
                            print(f"  {j}. Map to '{match}' (Score: {score})")  # Display the full match

                        while True:
                            match_choice = input("Enter the number for the mapping, or 'skip' to keep as is: ")
                            if match_choice.lower() == 'skip':
                                break
                            elif match_choice.isdigit():
                                match_index = int(match_choice)
                                if 0 <= match_index < len(matched_columns[selected_column]):
                                    chosen_mapping = matched_columns[selected_column][match_index][0]
                                    df.rename(columns={selected_columntemp: chosen_mapping}, inplace=True)
                                    selected_columntemp = df.columns.tolist()[column_index]
                                    print(f"Column {column_index}: '{selected_columntemp}' has been mapped to '{chosen_mapping}'.")
                                    break
                                else:
                                    print("Invalid input. Please enter a valid number.")
                            else:
                                print("Invalid input. Please enter a valid number or 'skip'.")
                        execution = False
                    else:
                        print("Invalid input, please choose a number or a list of numbers corresponding to a column")
            

            else:
                print("No reference columns loaded. Please check the reference columns file.")
                execution = False
        print("Mapping and cleanup finished. Updated DataFrame:")
        print(df)

# Configuración de la aplicación
st.title('Aplicación de Mapeo de Columnas')
st.write('Carga un archivo Excel y mapea las columnas con las de referencia.')

uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        df = None

    if df is not None:
        st.subheader('Vista previa de los datos:')
        st.write(df)

        reference_file = st.file_uploader("Subir archivo YAML de columnas de referencia", type=["yml", "yaml"])

        if reference_file is not None:
            with reference_file as file:
                try:
                    reference_columns = yaml.safe_load(file)
                except Exception as e:
                    st.error(f"Error al cargar las columnas de referencia: {str(e)}")
                    reference_columns = []

            if reference_columns:
                matched_columns = map_columns(df, reference_columns)

                st.subheader('Columnas mapeadas:')
                for column, mapping in matched_columns.items():
                    st.write(f"{column} -> {mapping}")

