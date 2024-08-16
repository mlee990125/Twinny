import streamlit as st
import pandas as pd
import json
from streamlit_lottie import st_lottie_spinner
from utils.data import get_data, process_chunk, clear_table, vrd

if 'chunk_counter' not in st.session_state:
    st.session_state.chunk_counter = 0

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

lottie_streamlit = load_lottiefile("./lottiefiles/CSV Upload Animation.json")
chunk_size = 1000
upload_option = st.radio(
        label="Choose One", options=["Add Additional Dataset", "Add Clean Dataset"], label_visibility="collapsed"
    )
uploaded_file = st.file_uploader("Upload new CSV file to database")
if uploaded_file is not None:
    st.write("filename: ", uploaded_file.name)
    with st_lottie_spinner(lottie_streamlit, height=300, key="uploading", speed=0.6):
        if upload_option == "Add Clean Dataset":
            clear_table()
        for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size):
            chunk = chunk.where(pd.notnull(chunk), None)
            process_chunk(chunk, vrd)
        st.write("Data processing and insertion completed.")
        if 'chunk_counter' in st.session_state:
            del st.session_state['chunk_counter']
        if 'date_range' in st.session_state:
            del st.session_state['date_range']
        get_data.clear()

st.subheader("Current Dataset: ")
st.write(get_data())