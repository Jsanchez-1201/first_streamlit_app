import streamlit as st

st.set_page_config(page_title="Welcome")

st.title("Marketing data cleaning app")

# Create a navigation menu
page = st.sidebar.selectbox("Select page 1 to start", ["Page 1", "Page 2"])

if page == "Page 1":
    st.title("Page 1: Upload DataFrame and Initial Mapping")
    import pages.page1
    pages.page1.page_1()
elif page == "Page 2":
    st.title("Page 2: Manual Column Modification and Updated DataFrame")
    import pages.page2
    pages.page2.page_2()
