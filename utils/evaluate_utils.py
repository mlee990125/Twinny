from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import streamlit as st
import pandas as pd
from streamlit_elements import elements, mui, nivo
from utils.common_utils import custom_colors, custom_theme, time_func
from konlpy.tag import Okt
from gensim import corpora
from gensim.models.ldamodel import LdaModel
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import json

@time_func
def get_similarity_score_list(data, bin_width):
    min_score = data['similarity_score'].min()
    max_score = data['similarity_score'].max()
    bins = np.arange(min_score, max_score + bin_width, bin_width)
    data['binned_similarity'] = pd.cut(data['similarity_score'], bins=bins, include_lowest=True)
    binned_counts = data['binned_similarity'].value_counts().sort_index()
    result = [{'similarity_score': f"{round(interval.left, 2)} ~ {round(interval.right, 2)}", 'count': count} 
            for interval, count in binned_counts.items()]
    return result

@time_func
def compute_similarities(data):
    # Convert embeddings to numpy arrays if they're not already
    query_embeddings = np.array(data["query_embedding"].tolist())
    response_embeddings = np.array(data["response_embedding"].tolist())

    # Compute cosine similarity
    similarities = np.diag(cosine_similarity(query_embeddings, response_embeddings))

    return similarities

def display_similarity_histogram(similarity_score_list):
    with elements("simlarity_histogram"):
        with mui.Box(sx={"height": 500}):
            nivo.Bar(
                data=similarity_score_list,
                keys=["count"],
                indexBy="similarity_score",
                margin={"top": 20, "right": 20, "bottom": 30, "left": 30},
                padding={0.3},
                valueScale={"type": "linear"},
                indexScale={"type": "band", "round": True},
                colors=custom_colors,
                borderColor={"from": "color", "modifiers": [["darker", 1.6]]},
                axisTop=None,
                axisRight=None,
                axisBottom={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "tickRotation": 0,
                    "legendPosition": "middle",
                    "legendOffset": 32,
                    "truncateTickAt": 0,
                    "tickValues": (
                        [item["similarity_score"]]
                        for item in [
                            similarity_score_list[i]
                            for i in range(0, len(similarity_score_list), 5)
                        ]
                    ),
                },
                axisLeft={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "tickRotation": 0,
                    "legendPosition": "middle",
                    "legendOffset": -40,
                    "truncateTickAt": 0,
                    "tickValues": 5,
                },
                labelSkipWidth=12,
                labelSkipHeight=12,
                labelTextColor={"from": "color", "modifiers": [["darker", 1.6]]},
                label={lambda d: ""},
                theme=custom_theme,
            )

def display_samples(category_data, category_name):
    st.subheader(f"{category_name}")
    sample = category_data.sample(2) if len(category_data) >= 5 else category_data
    for _, row in sample.iterrows():
        st.write(f"Query: {row['user_query']}")
        st.write(f"Response: {row['response']}")
        st.write(f"Similarity Score: {row['similarity_score']:.4f}")
        st.write("--")

@st.cache_data
def unique_word_ratio(text):
    okt = Okt()
    words = okt.morphs(text)
    return len(set(words)) / len(words) if words else 0

@st.cache_data
def preprocess(text):
    okt = Okt()
    return [word for word in okt.nouns(text) if len(word) > 1]

@st.cache_data
def preprocess_data(data):
    return [preprocess(text) for text in data["response"]]

@st.cache_resource
def create_dictionary(corpus):
    return corpora.Dictionary(corpus)

@st.cache_resource
def create_bow_corpus(corpus, _dictionary):
    return [_dictionary.doc2bow(text) for text in corpus]

@st.cache_resource
def create_lda_model(bow_corpus, _dictionary, num_topics, passes):
    return LdaModel(bow_corpus, num_topics=num_topics, id2word=_dictionary, passes=passes)


@time_func
def get_lda_model(data, num_topics, passes):
    corpus = preprocess_data(data)
    dictionary = create_dictionary(corpus)
    bow_corpus = create_bow_corpus(corpus, _dictionary=dictionary)
    lda_model = create_lda_model(bow_corpus, _dictionary=dictionary, num_topics=num_topics, passes=passes)
    return lda_model


def prepare_topic_data(lda_model, num_words):
    all_topics_data = []
    for idx, topic in lda_model.print_topics(-1):
        topic_data = []
        words = topic.split(" + ")
        for word_weight in words[:num_words]:
            weight, word = word_weight.split("*")
            word = word.strip()[1:-1]  # Remove quotes
            weight = float(weight)
            topic_data.append({"id": word, "label": word, "value": weight})
        all_topics_data.append({"topic": f"Topic {idx}", "data": topic_data})
    return all_topics_data

def make_topic_pie(topic_data, i):
    with elements(f"topic_model_pie_{i}"):
        with mui.Box(sx={"height": 300}):
            nivo.Pie(
                data=topic_data[i]["data"],
                margin={"top": 20, "right": 10, "bottom": 20, "left": 10},
                innerRadius=0.65,
                padAngle=2,
                cornerRadius=3,
                activeOuterRadiusOffset=8,
                borderWidth=1,
                colors=custom_colors,
                borderColor={"from": "color", "modifiers": [["darker", 0.2]]},
                arcLinkLabelsSkipAngle=10,
                arcLinkLabelsTextColor="#EEEEEE",
                arcLinkLabelsThickness=2,
                arcLinkLabelsColor={"from": "color"},
                arcLabelsSkipAngle=10,
                arcLabelsTextColor="#EEEEEE",
                arcLinkLabelsStraightLength=5,
                arcLinkLabelsDiagonalLength=10,
                enableArcLabels=False,
                enableArcLinkLabels=True,
                arcLabel="id",
                theme=custom_theme,
            )

@time_func
def check_response_consistency(df):
    results = []
    for query, group in df.groupby("user_query"):
        # Get unique responses and their embeddings
        unique_responses = group.drop_duplicates(subset=["response"])
        if (
            len(unique_responses) >= 2
        ):  # Only process groups with at least 2 unique responses
            embeddings = np.stack(unique_responses["response_embedding"].values)
            
            similarities = cosine_similarity(embeddings)
            # Get upper triangle of similarity matrix (excluding diagonal)
            upper_tri = similarities[np.triu_indices(similarities.shape[0], k=1)]
            results.append(
                {
                    "user_query": query,
                    "total_responses": len(group),
                    "unique_responses_count": len(unique_responses),
                    "mean_similarity": np.mean(upper_tri),
                    "min_similarity": np.min(upper_tri),
                    "max_similarity": np.max(upper_tri),
                    "std_similarity": np.std(upper_tri),
                    "pairwise_similarities": upper_tri.tolist(),
                    "unique_responses": unique_responses["response"].tolist(),
                }
            )
    return pd.DataFrame(results)

def highlight_inconsistent(row):
    styles = [""] * len(row)
    if (
        isinstance(row["mean_similarity"], (int, float))
        and row["mean_similarity"] < 0.5
    ):
        styles[row.index.get_loc("mean_similarity")] = "background-color: steelblue"
    if (
        isinstance(row["min_similarity"], (int, float))
        and row["min_similarity"] < 0.3
    ):
        styles[row.index.get_loc("min_similarity")] = "background-color: steelblue"
    return styles

def extract_coordinates(status_str):
    try:
        status_dict = json.loads(status_str.replace("'", '"'))
        location = status_dict.get("location", {})
        return location.get("lat"), location.get("lon")
    except:
        return None, None

@time_func
def draw_heatmap(data, padding):
    x_min, x_max = data["x"].min() - padding, data["x"].max() + padding
    y_min, y_max = data["y"].min() - padding, data["y"].max() + padding

    m = folium.Map(
        location=[(y_min + y_max) / 2, (x_min + x_max) / 2],
        zoom_start=1,
        tiles=None,
        attr="Custom map",
    )

    folium.Rectangle(
        bounds=[[y_min + padding, x_min + padding], [y_max - padding, x_max - padding]],
        color="black",
        fill=False,
        weight=2,
    ).add_to(m)

    # Add grid lines
    num_lines = 10
    for i in range(num_lines + 1):
        folium.PolyLine(
            [
                [
                    y_min + padding,
                    x_min + padding + i * (x_max - x_min - 2 * padding) / num_lines,
                ],
                [
                    y_max - padding,
                    x_min + padding + i * (x_max - x_min - 2 * padding) / num_lines,
                ],
            ],
            color="grey",
            weight=0.5,
            opacity=0.5,
        ).add_to(m)
        folium.PolyLine(
            [
                [
                    y_min + padding + i * (y_max - y_min - 2 * padding) / num_lines,
                    x_min + padding,
                ],
                [
                    y_min + padding + i * (y_max - y_min - 2 * padding) / num_lines,
                    x_max - padding,
                ],
            ],
            color="grey",
            weight=0.5,
            opacity=0.5,
        ).add_to(m)

    # Create the heatmap layer
    heat_data = [
        [
            max(y_min + padding, min(y_max - padding, row["y"])),
            max(x_min + padding, min(x_max - padding, row["x"])),
        ]
        for _, row in data.iterrows()
    ]
    HeatMap(heat_data, min_opacity=0.5, max_opacity=0.8, radius=15).add_to(m)

    # Fit the map to the data bounds
    m.fit_bounds([[y_min, x_min], [y_max, x_max]])

    # Add X-axis labels
    for i in range(num_lines + 1):
        x = x_min + i * (x_max - x_min - 2 * padding) / num_lines + padding
        folium.Marker(
            [y_min, x],
            icon=folium.DivIcon(html=f'<div style="font-size: 10pt">{x:.1f}</div>'),
        ).add_to(m)

    # Add Y-axis labels
    for i in range(num_lines + 1):
        y = y_min + i * (y_max - y_min - 2 * padding) / num_lines + padding
        folium.Marker(
            [y, x_min],
            icon=folium.DivIcon(html=f'<div style="font-size: 10pt">{y:.1f}</div>'),
        ).add_to(m)

    # Display the map
    st.header("Robot Activity Heatmap")
    folium_static(m, width=1300, height=600)