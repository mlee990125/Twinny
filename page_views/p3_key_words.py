import streamlit as st
from streamlit_lottie import st_lottie_spinner

from utils.common_utils import load_lottiefile, load_data, return_keyword_df
from utils.key_word_utils import draw_graph


# Load Lottie animation 
lottie_streamlit = load_lottiefile("./lottiefiles/Data Loading Animation.json")

def main():
    # Title
    st.title("Key Words")
    with st.expander("Key Word Search Overview"):
        st.write(
            """
            The "Key Word Search" section of the dashboard provides an interactive tool to visualize the relationships between keywords in user queries and responses. 
            This visualization is achieved using a node graph, where connections (edges) between keywords are shown, and the weight of these edges represents the frequency 
            of keyword co-occurrences.

            ### Features:
            - Keyword Visualization: Displays a node graph that highlights the connections between keywords from queries and responses. 
            - Stemming Option: Includes a toggle option to enable or disable the stemming of nouns, allowing for more refined keyword analysis.
            - Dynamic Data Display: Users can adjust the number of queries and responses displayed using sliders.
            - Word Search: Provides an option to search for individual keywords within the queries or responses. 
        """
        )
    # Load data
    data = load_data()
    if len(data) > 0:
        # Toggler for stemming
        on = st.toggle("Stem Nouns", key="key1")
        keyword_df = return_keyword_df(on, data)

        # Slider for number of queries and responses
        max_rows = keyword_df.shape[0]
        max_columns = keyword_df.shape[1]
        number_of_rows = 10
        number_of_columns = 10

        # Sidebar options
        with st.sidebar:
            number_of_rows = st.slider(
                label=f"Select Number of Responses:",
                step=1,
                min_value=1,
                max_value=max_rows,
                value=10,
            )
            number_of_columns = st.slider(
                label=f"Select Number of Queries:",
                step=1,
                min_value=1,
                max_value=max_columns,
                value=10,
            )

        # Display Query - Response visualization by table
        keyword_df = keyword_df.head(number_of_rows).iloc[:, :number_of_columns]

        # Option for view in node graph, create a word_bank off choice
        option = st.radio(
            label="Choose One", options=["Query", "Response"], label_visibility="collapsed"
        )
        if option == "Query":
            word_bank = tuple(keyword_df.columns.tolist())
        elif option == "Response":
            word_bank = tuple(keyword_df.index.tolist())

        # Word Search    
        select_word = st.selectbox(
            label="Enter a word...",
            options=word_bank,
            placeholder="Enter a word...",
            label_visibility="collapsed",
        )

        # Draw the node graph
        draw_graph(option, select_word, keyword_df)

        st.subheader("Data Set (Rows: Responses, Columns: User Queries)")
        st.write(keyword_df)
    else:
        st.write("No Data Found")


with st_lottie_spinner(lottie_streamlit, height=800, key="loading"):
    main()
