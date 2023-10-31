import streamlit as st
import pandas as pd
import fuzzywuzzy.process as fuzz
import re
import yaml

# Función para encontrar y emparejar columnas
def match_columns(df, reference_columns):
    matched_columns = {}  # Inicializar el diccionario de columnas emparejadas

    input_columns = df.columns.tolist()

    for column in input_columns:
        matches = fuzz.extractBests(column, reference_columns)
        if matches:
            matched_columns[column] = matches

    return matched_columns

# Configuración de la aplicación
st.title('Aplicación de Mapeo de Columnas y Limpieza de Datos')
st.write('Carga un archivo Excel y mapea las columnas con las de referencia. Luego, permite al usuario realizar modificaciones en las columnas.')

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
                matched_columns = match_columns(df, reference_columns)

                st.subheader('Columnas mapeadas:')
                for column, mapping in matched_columns.items():
                    st.write(f"{column} -> {mapping}")

                # Eliminar las columnas que no están en reference_columns
                columns_to_remove = [col for col in df.columns if col not in reference_columns]
                df.drop(columns=columns_to_remove, inplace=True)

                # Verificar si "Last Name" no existe y crearlo
                if "Last Name" not in df.columns:
                    df["Last Name"] = ""

                # Permitir al usuario especificar columnas para modificación
                st.subheader('Modificación de Columnas')
                change_columns_input = st.text_input("Ingrese una lista de columnas para modificar (e.g., '0, 5, 7') o 'none' para omitir:")

                if change_columns_input.lower() != 'none':
                    change_columns_list = [int(col.strip()) for col in change_columns_input.split(',') if col.strip()]
                    for column_index in change_columns_list:
                        if 0 <= column_index and column_index < len(matched_columns):
                            selected_column = list(matched_columns.keys())[column_index]
                            st.write(f"Opciones de mapeo para la columna {column_index}: '{selected_column}':")
                            for j, (match, score) in enumerate(matched_columns[selected_column]):
                                st.write(f"  {j}. Mapear a '{match}' (Puntuación: {score})")  # Mostrar la coincidencia completa
                            match_choice = st.text_input("Ingrese el número del mapeo o 'skip' para mantener como está:")
                            if match_choice.lower() != 'skip' and match_choice.isdigit():
                                match_index = int(match_choice)
                                if 0 <= match_index < len(matched_columns[selected_column]):
                                    chosen_mapping = matched_columns[selected_column][match_index][0]
                                    df.rename(columns={selected_column: chosen_mapping}, inplace=True)
                                    st.write(f"La columna {column_index}: '{selected_column}' se ha mapeado a '{chosen_mapping}'.")
                            else:
                                st.write("No se ha realizado ningún cambio en la columna.")
                        else:
                            st.write("Entrada no válida, elija un número o una lista de números que corresponda a una columna")

                st.subheader('DataFrame Actualizado:')
                st.write(df)
