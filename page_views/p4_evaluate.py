import streamlit as st
import plotly.express as px
from streamlit_lottie import st_lottie_spinner

from utils.common_utils import load_lottiefile, load_data, time_func
from utils.evaluate_utils import (
    get_similarity_score_list, 
    compute_similarities, 
    display_similarity_histogram, 
    display_samples, 
    unique_word_ratio, 
    get_lda_model, 
    prepare_topic_data, 
    make_topic_pie,
    check_response_consistency,
    highlight_inconsistent,
    extract_coordinates,
    draw_heatmap
)


# Load Lottie animation
lottie_streamlit = load_lottiefile("./lottiefiles/Data Loading Animation.json")


def main():
    # Load data
    data = load_data()
    # Compute similarities
    if len(data) > 0:
        data["similarity_score"] = compute_similarities(data)

        # **Display Query-Response Similarity Score Histogram**
        st.header("Query-Response Similarity Score Distribution")
        similarity_score_list = get_similarity_score_list(data, bin_width=0.02)
        display_similarity_histogram(similarity_score_list)
        
        # Average Similarity
        average_similarity = data["similarity_score"].mean()
        st.write(f"Average similarity score of: ***{average_similarity:.4f}***")

        st.divider()

        # **Response Coherence**
        st.header("Response Coherence")
        with st.expander("Response Coherence Overview"):
            st.write(
                f"""
                The coherence of a response to a given query is determined using cosine similarity values of the query and response embeddings. 
                Higher similarity scores indicate greater relevance. Responses identical to the query will have a perfect similarity score (parroting), 
                so we use specific thresholds to classify responses as parroting, coherent, or incoherent.

                The classification thresholds are as follows:
                - **Parroting**: 0.95 ≤ Similarity Score ≤ 1.00
                - **Coherent Response**: 0.30 ≤ Similarity Score < 0.95
                - **Incoherent Response**: 0.00 ≤ Similarity Score < 0.30

                The threshold of 0.30 for coherence was selected based on human observation to ensure meaningful and relevant responses.
                Given that the average similarity score of the responses is {average_similarity:.4f}, we can assess that the model is coherent on average.

                Below gives two samples of each classification. Press "Resample" to resample the similarity dataset.
            """
            )

        # Classify Coherence
        parroting = data[data["similarity_score"] >= 0.95]
        coherent = data[
            (data["similarity_score"] >= 0.3) & (data["similarity_score"] < 0.95)
        ]
        incoherent = data[data["similarity_score"] < 0.3]

        # Resample button
        if st.button("Resample"):
            parroting = parroting.sample(frac=1).reset_index(drop=True)
            coherent = coherent.sample(frac=1).reset_index(drop=True)
            incoherent = incoherent.sample(frac=1).reset_index(drop=True)

        # Display samples for each category
        col1, col2, col3 = st.columns(3)
        with col1:
            display_samples(parroting, "Parroting")
        with col2:
            display_samples(coherent, "Coherent Response")
        with col3:
            display_samples(incoherent, "Incoherent Response")

        st.divider()

        # **Lexical Diversity**
        st.header("Lexical Diversity")
        st.write(
            f"""
            Lexical diversity is the measure of how varied the vocabulary is within a given text. Type-Token Ratio (TTR) is used to calculate the lexical diversity.  
            It simply checks the ratio of unique words (types) in the text to the total number (tokens) of words. A Korean specific morphological analyzer KoNLPy was 
            used for tokenization. 
            """
        )
        ttr_code = """
        from konlpy.tag import Okt

        okt = Okt()
        def unique_word_ratio(text):
            words = okt.morphs(text)
            return len(set(words)) / len(words) if words else 0
        """
        st.code(ttr_code, language="python")

        # Compute word_diversty
        if len(data) > 100:
            data["word_diversity"] = data.sample(100)["response"].apply(unique_word_ratio)
        else:
            data["word_diversity"] = data["response"].apply(unique_word_ratio) 
    
        st.write(
            f"""
            Due to long computation time, a sample of 100 rows were used to find that the average TTR value of responses using a morphological analyzer was ***{data['word_diversity'].mean():.4f}***  
            """
        )
        
        st.divider()

        # **Topic Modeling**
        st.header("Topic Modeling")
        with st.expander("Topic Modeling Overview"):
            st.write(
                f"""
                The Topic Modeling aims to identify key words to caputre the topics within the response texts. This process involves the following steps:  


                - Text Preprocessing:
                    - The responses are processed to extract nouns using the Okt (Open Korean Text) tokenizer.
                    - Only nouns with more than one character are retained to ensure meaningful topics.  

                ------------------------------
                - Corpus Creation:
                    - A sample of 500 responses is taken for analysis.
                    - The preprocessed text is converted into a format suitable for topic modeling.  

                ------------------------------
                - Dictionary and Bag-of-Words (BoW) Generation:
                    - A dictionary is created from the corpus, mapping each unique word to an ID.
                    - The corpus is transformed into a Bag-of-Words format, which counts the occurrences of each word in each response.  

                ------------------------------
                - Latent Dirichlet Allocation (LDA) Model:
                    - An LDA model is trained using the Bag-of-Words corpus.
                    - The model identifies 6 distinct topics within the responses by iterating over the data 20 times (passes).      
            """
            )
        topic_modeling_code = """
        from gensim import corpora
        from gensim.models.ldamodel import LdaModel
        
        def preprocess(text):
            return [word for word in okt.nouns(text) if len(word) > 1]
        
        corpus = [preprocess(text) for text in data.sample(500)['response']]
        dictionary = corpora.Dictionary(corpus)
        bow_corpus = [dictionary.doc2bow(text) for text in corpus]

        lda_model = LdaModel(bow_corpus, num_topics=6, id2word=dictionary, passes=20)

        """
        st.code(topic_modeling_code, language="python")

        # LDA Model
        if len(data) > 500:
            lda_data = data.sample(500, random_state=42)
        else: lda_data = data

        lda_model = get_lda_model(data=lda_data, num_topics=6, passes=10)

        # Generate the data
        topic_data = prepare_topic_data(lda_model, num_words=5)

        # Display topic pie charts
        col1_tm, col2_tm = st.columns(2)
        for i in range(6):
            col = col1_tm if i % 2 == 0 else col2_tm
            with col:
                st.write(f"Topic {i+1}: ")
                make_topic_pie(topic_data, i)

        st.divider()

        # **Response Consistency**
        consistency_results = check_response_consistency(data)
        if len(consistency_results) > 0:
            sorted_results = consistency_results.sort_values(
                ["unique_responses_count", "mean_similarity"], ascending=[False, False]
            )
            response_counts = data.groupby("user_query")["response"].nunique()
            single_response_count = (response_counts == 1).sum()
            multi_resposne_count = (consistency_results["unique_responses_count"] > 1).sum()
            single_response_percentage = (single_response_count / len(response_counts)) * 100

            st.header("Response Consistency")
            with st.expander("Response Consistency Overview"):
                st.write(
                    f"""
                    ### Key Features:
                    This data analyzes unique responses of length > 1 of unique queries. As ***{100 - single_response_percentage:.2f}%*** of all unique queries had responses > 1, ***{multi_resposne_count}*** responses were analyzed.

                    #### Data Processing:
                    - Preprocessing: The responses are grouped by their corresponding queries.
                    - Unique Responses: For each query, duplicate responses are removed to identify unique responses.
                    
                    #### Similarity Computation:
                    - Cosine Similarity: The cosine similarity between the embeddings of unique responses is computed to measure how similar the responses are to each other.
                    - Similarity Metrics: Various similarity metrics are calculated:
                        - Mean, Min, Max,  Standard Deviation
                    #### Identifying Inconsistencies:
                    - Queries with potentially inconsistent responses are highlighted based on their similarity scores:
                        - Mean Similarity < 0.5: Indicates general inconsistency.
                        - Minimum Similarity < 0.3: Indicates at least one highly inconsistent response.
                    #### Visualizations:
                    - Mean Similarity vs. Unique Response Count Scatter Plot: A scatter plot showing the relationship between the number of unique responses and their average similarity.
                    - Inconsistent Response Scatter Plot: A scatter plot for queries with potential inconsistencies, highlighting the relationship between the lowest and average similarity scores.
                    #### Data Table with Highlights:
                    - A styled data table displays the top 50 queries with their corresponding similarity metrics. Inconsistent responses are highlighted for easy identification.
                    #### Detailed Query Examination:
                    - Users can input a specific query to examine all unique responses and their similarity scores, providing a deeper understanding of the response consistency for that particular query.
                    """
                )

            # Find queries with potentially inconsistent responses
            inconsistent_queries = consistency_results[
                (consistency_results["mean_similarity"] < 0.5)
                | (consistency_results["min_similarity"] < 0.3)
            ]

            # Similarity Scatter Plot
            st.subheader("Mean Similarity vs. Unique Response Count (>2) Scatter Plot")
            fig = px.scatter(
                consistency_results,
                x="unique_responses_count",
                y="mean_similarity",
                hover_data=["user_query"],
            )
            st.plotly_chart(fig)

            # Inconsistent Scatter Plot
            st.subheader("Inconsistent Response Scatter Plot")
            fig = px.scatter(
                inconsistent_queries,
                x="mean_similarity",
                y="min_similarity",
                size="unique_responses_count",
                hover_data=["user_query"],
            )
            st.plotly_chart(fig)

            # Display dataframe with inconsistency highlighted
            df_to_display = sorted_results[
                [
                    "user_query",
                    "unique_responses_count",
                    "mean_similarity",
                    "min_similarity",
                    "max_similarity",
                    "std_similarity",
                ]
            ].head(50)

            styled_df = df_to_display.style.apply(highlight_inconsistent, axis=1)
            st.subheader("Response Consistency DF (Inconsistent Responses Highlighted)")
            st.dataframe(styled_df)

            # Search for Query of Interest
            query_of_interest = st.text_input(
                label="Query of interest",
                value=None,
                placeholder="Type a Query...",
                label_visibility="collapsed",
            )
            if query_of_interest:
                if query_of_interest in consistency_results['user_query'].values:
                    query_data = consistency_results[
                        consistency_results["user_query"] == query_of_interest
                    ].iloc[0]
                    
                    st.write(f"Responses for '{query_of_interest}':")
                    for i, response in enumerate(query_data["unique_responses"], 1):
                        st.write(f"Response {i}: {response}")
                else:
                    st.write(f"No responses found for '{query_of_interest}'.")
            st.divider()

        # **Robot Activity Heatmap**
        data["x"], data["y"] = zip(*data["status"].apply(extract_coordinates))
        data = data.dropna(subset=["x", "y"])
        padding = 2 

        # Display Heatmap
        draw_heatmap(data, padding)
    else:
        st.write("No Data Found")

with st_lottie_spinner(lottie_streamlit, height=800, key="loading"):
    main()
    print("---------")
