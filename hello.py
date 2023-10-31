import streamlit as st
import pandas as pd
import fuzzywuzzy.process as fuzz
import re
import yaml

# Función para mapear columnas
def map_columns(df, reference_columns):
    matched_columns = {}
    input_columns = df.columns.tolist()

    for column in input_columns:
        matches = fuzz.extractBests(column, reference_columns)
        if matches:
            matched_columns[column] = matches

    return matched_columns

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
                    st.error(f"Error al cargar las columnas de referencia: {str(e}")
                    reference_columns = []

            if reference_columns:
                matched_columns = map_columns(df, reference_columns)

                st.subheader('Columnas mapeadas:')
                for column, mapping in matched_columns.items():
                    st.write(f"{column} -> {mapping}")

                # Aquí puedes realizar otras operaciones con los datos mapeados si es necesario
