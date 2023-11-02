import streamlit as st
import pandas as pd

# Page 2: Manual Column Modification and Updated DataFrame
def page_2():
    df = st.session_state.df  # Retrieve the DataFrame from session state

    if df is not None:
        st.subheader('Data Preview:')
        st.write(df)

        st.subheader('Manual Column Modification')
        # Implement the manual column modification functionality here

        # Display the updated DataFrame
        st.subheader('Updated DataFrame:')
        st.write(df)
