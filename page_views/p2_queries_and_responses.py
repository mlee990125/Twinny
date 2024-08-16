import streamlit as st
from streamlit_lottie import st_lottie_spinner
from streamlit_elements import elements

from components.component_window import Window
from components.component_pie import Pie
from components.component_bar_horizontal import Bar_Horizontal
from components.component_card import Card
from utils.common_utils import (
    load_lottiefile,
    load_data
)
from utils.queries_and_responses_utils import (
    calculate_keyword_data,
    calculate_kmeans_clustering,
    prepare_pie_chart_data,
    calculate_avg_unique_responses
)


# Custom CSS for styling
custom_css = """
    <style>
    
    /* Adjust the padding around the main content area */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    /* Optional: Adjust the padding around the sidebar */
    .sidebar .sidebar-content {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
    """
st.markdown(custom_css, unsafe_allow_html=True)

# Load Lottie animation
lottie_streamlit = load_lottiefile("./lottiefiles/Data Loading Animation.json")


def main():
    # Queries and Responses overview expander
    with st.expander("Queries and Responses Overview"):
        st.write(
            """
            ### Key Features:  
            #### Top 5 Query/Response Keywords (Bar Graph):  
            - Displays the most frequently occurring keywords in the queries and responses, tokenized and visualized for easy comparison.  

            #### Query/Response K-means Clustering (Pie Chart):  
            - Illustrates the clusters identified within the queries and responses using K-means clustering.  
            - The KR-SBERT sentence transformers model encodes embeddings for each query/response. Cosine similarity is then used to determine the clusters.  

            
            #### Customizable Date Range:  
            - Use the date selector in the left sidebar to filter the data within the available time range.  

            #### Representative Sentence Type:  
            - Adjust the representative sentence of the clusters shown in the pie chart using the "Representative Sentence Type" dropdown menu on the left sidebar. Options include:  
                - Central
                - Frequent
                - Shortest
                - Medoid  

            #### Adjustable Number of Clusters:  
            - Change the number of K clusters by inputting a different value in the "Number of K Clusters" field on the left sidebar.
                    
        """
        )

    # Load data
    data = load_data()
    if len(data) > 0:
        # Sidebar options
        with st.sidebar:
            representative_type = st.selectbox(
                "Representative Sentence Type",
                (
                    "Most Central Sentence",
                    "Most Frequent Sentence",
                    "Shortest Sentence",
                    "Medoid Sentence",
                ),
            )
            num_clusters = st.number_input(
                label="Number of K Clusters", min_value=1, max_value=15, value=12, step=1
            )
        
        # Prepare data for draggable elements
        top_5_q_words, top_5_r_words = calculate_keyword_data(data)
        q_representative_sentences, r_representative_sentences = calculate_kmeans_clustering(data, num_clusters, representative_type)
        pie_q_data = prepare_pie_chart_data(data, q_representative_sentences, "q_k_cluster_label")
        pie_r_data = prepare_pie_chart_data(data, r_representative_sentences, "r_k_cluster_label")
        
        # Create draggable elements
        with elements("queries-and-responses"):
            board = Window()

            q_pie = Pie(
                board, 0, 2, 6, 3, pie_data=pie_q_data,
                title="Query Kmeans Clustering", minW=1, minH=1
                )
            
            r_pie = Pie(
                board, 6, 2, 6, 3, pie_data=pie_r_data,
                title="Response Kmeans Clustering", minW=1, minH=1
                )
            
            top_5_q_bar = Bar_Horizontal(
                board, 0, 0, 4, 2, data=top_5_q_words,
                title="Top 5 Query Keywords", minW=1, minH=1
                )
            
            top_5_r_bar = Bar_Horizontal(
                board, 4, 0, 4, 2, data=top_5_r_words,
                title="Top 5 Response Keywords", minW=1, minH=1
                )
            
            query_avg_card = Card(
                board, 8, 0, 2, 1,
                title="Avg Query Length", value=f"{data['user_query'].str.len().mean():.2f}",
                subtitle="Avg Query Length", minW=1, minH=1
                )
            
            response_avg_card = Card( 
                board, 8, 1, 2, 1,
                title="Avg Response Length", value=f"{data['response'].str.len().mean():.2f}",
                subtitle="Avg Response Length", minW=1, minH=1
                )
            
            uniq_response_avg_card = Card(
                board,10, 0, 2, 2,
                title="Avg Unique Responses/Query", value=f"{calculate_avg_unique_responses(data):.2f}",
                subtitle="Avg Unique Responses/Query", minW=1, minH=1
                )

            with board():
                q_pie()
                r_pie()
                top_5_q_bar()
                top_5_r_bar()
                query_avg_card()
                response_avg_card()
                uniq_response_avg_card()
    else:
        st.write("No Data Found")

with st_lottie_spinner(lottie_streamlit, height=800, key="loading"):
    main()
