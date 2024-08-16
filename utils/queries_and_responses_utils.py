import numpy as np
import streamlit as st
import time
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from utils.common_utils import  return_keyword_df, time_func


def most_central_sentences(data, clusters, embeddings, option):
    representatives = {}
    for cluster in set(clusters):
        cluster_mask = clusters == cluster
        cluster_embeddings = embeddings[cluster_mask]
        if option == 'q':
            cluster_sentences = data.loc[cluster_mask, 'user_query'].tolist()
        elif option =='r':
            cluster_sentences = data.loc[cluster_mask, 'response'].tolist()
        
        # Calculate centroid
        centroid = np.mean(cluster_embeddings, axis=0)
        
        # Find the sentence closest to the centroid
        similarities = cosine_similarity([centroid], cluster_embeddings)[0]
        representative_idx = np.argmax(similarities)
        
        representatives[cluster] = cluster_sentences[representative_idx]
    
    return representatives

def most_frequent_sentences(data, clusters, option):
    representatives = {}
    for cluster in set(clusters):
        if option == 'q':
            cluster_sentences = data.loc[clusters == cluster, 'user_query'].tolist()
        elif option == 'r':
            cluster_sentences = data.loc[clusters == cluster, 'response'].tolist()
        most_common = Counter(cluster_sentences).most_common(1)
        representatives[cluster] = most_common[0][0] if most_common else None
    
    return representatives


def shortest_sentences(data, clusters, option):
    representatives = {}
    for cluster in set(clusters):
        if option == 'q':
            cluster_sentences = data.loc[clusters == cluster, 'user_query'].tolist()
        elif option == 'r':
            cluster_sentences = data.loc[clusters == cluster, 'response'].tolist()
        shortest = min(cluster_sentences, key=len)
        representatives[cluster] = shortest
    
    return representatives


def medoid_sentences(data, clusters, embeddings, option):
    representatives = {}
    for cluster in set(clusters):
        cluster_mask = clusters == cluster
        cluster_embeddings = embeddings[cluster_mask]
        if option == 'q':
            cluster_sentences = data.loc[cluster_mask, 'user_query'].tolist()
        elif option == 'r':
            cluster_sentences = data.loc[cluster_mask, 'response'].tolist()
        
        # Calculate pairwise similarities
        similarities = cosine_similarity(cluster_embeddings)
        
        # Find the sentence with highest average similarity to others
        medoid_idx = np.argmax(np.mean(similarities, axis=1))
        
        representatives[cluster] = cluster_sentences[medoid_idx]
    
    return representatives


@st.cache_data
def get_representative_sentences(data, clusters, embeddings, option, representative_type):
    if representative_type == "Most Central Sentence":
        return most_central_sentences(data, clusters, embeddings, option)
    elif representative_type == "Most Frequent Sentence":
        return most_frequent_sentences(data, clusters, option)
    elif representative_type == "Shortest Sentence":
        return shortest_sentences(data, clusters, option)
    elif representative_type == "Medoid Sentence":
        return medoid_sentences(data, clusters, embeddings, option)
    

@time_func
@st.cache_data
def get_kmeans_clusters(option, data, n_clusters):
    if option == "q":
        embeddings = np.stack(data["query_embedding"].to_numpy())
    elif option == "r":
        embeddings = np.stack(data["response_embedding"].to_numpy())
    
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    clusters = kmeans.fit_predict(embeddings)
    return clusters

def calculate_keyword_data(data):
    keyword_df = return_keyword_df(False, data)
    top_5_q_words = keyword_df.sum(axis=0).sort_values(ascending=False).head(5)
    top_5_r_words = keyword_df.sum(axis=1).sort_values(ascending=False).head(5)
    return top_5_q_words, top_5_r_words

def calculate_kmeans_clustering(data, num_clusters, representative_type):
    if len(data) < 12:
        num_clusters = len(data)
    data["q_k_cluster_label"] = get_kmeans_clusters("q", data, num_clusters)
    data["r_k_cluster_label"] = get_kmeans_clusters("r", data, num_clusters)

    q_embeddings = np.stack(data["query_embedding"].to_numpy())
    r_embeddings = np.stack(data["response_embedding"].to_numpy())

    q_representative_sentences = get_representative_sentences(
        data, data["q_k_cluster_label"], q_embeddings, "q", representative_type
    )

    r_representative_sentences = get_representative_sentences(
        data, data["r_k_cluster_label"], r_embeddings, "r", representative_type
    )

    return q_representative_sentences, r_representative_sentences

def prepare_pie_chart_data(data, representative_sentences, label_col):
    label_counts = data[label_col].value_counts().reset_index()
    label_counts.columns = ["id", "value"]
    label_counts = label_counts.sort_values(by="id")

    pie_data = [
        {
            "id": representative_sentences[(row["id"])],
            "label": "Cluster " + str(row["id"]),
            "value": int(row["value"]),
        }
        for _, row in label_counts.iterrows()
    ]
    return pie_data

def calculate_avg_unique_responses(data):
    # Group by query and count unique responses
    unique_responses_per_query = data.groupby('user_query')['response'].nunique()
    
    # Calculate the average
    avg_unique_responses = unique_responses_per_query.mean()
    
    return avg_unique_responses
