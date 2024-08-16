import streamlit as st
import pandas as pd
import json
from utils.data import get_data
from collections import Counter
import re
import time
from streamlit_extras.mandatory_date_range import date_range_picker

custom_colors = ['#5db89d', '#399291', '#2e6c79', '#2c4857', '#222831']
# ["#76ABAE", "#5A9BA8", "#4B8797", "#3C7386", "#2E5F75", "#1F4B64"]

custom_theme = {
    "axis": {
        "ticks": {
            "text": {
                "fontSize": 12,
                "fill": "#F8FBFE",
            }
        },
        "legend": {
            "text": {
                "fontSize": 12,
                "fill": "#cccccc",
            }
        },
    },
    "labels": {
        "text": {
            "fontSize": 12,
            "fill": "#cccccc",  
        }
    },
    "legends": {"text": {"fontSize": 12, "fill": "#cccccc"}},
    "tooltip": {
        "container": {
            "background": "#31363F",
            "color": "#EEEEEE",
            "fontSize": 12,
        }
    },
    "grid": {
        "line": {
            "stroke": "#666666",  
            "strokeWidth": 1
        }
    }
}

def load_data():
    data = get_data()
    data = date_range_selector(data)
    return data

def date_range_selector(data, timestamp_column="timestamp"):
    MIN_VALUE = data.iloc[0][timestamp_column]
    MAX_VALUE = data.iloc[-1][timestamp_column]

    if "date_range" in st.session_state and len(st.session_state["date_range"]) == 2:
        start_value, end_value = st.session_state["date_range"]
    else:
        start_value, end_value = MIN_VALUE, MAX_VALUE

    with st.sidebar:
        date_range = date_range_picker(
            title="Select Dates",
            default_start=start_value,
            default_end=end_value,
            min_date=MIN_VALUE,
            max_date=MAX_VALUE,
            error_message="Please select start and end date.",
            key="date_key"
        )
    if len(date_range) == 2:
        st.session_state["date_range"] = date_range
        filtered_data = data[
            (data[timestamp_column] >= pd.to_datetime(date_range[0]))
            & (
                data[timestamp_column]
                <= pd.to_datetime(date_range[1]) + pd.Timedelta(hours=24)
            )
        ]
        return filtered_data

    return data

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Function to tokenize and clean text
def tokenize(text):
    # Remove special characters and split by whitespace
    tokens = re.findall(r"\b\w+\b", text.lower())
    return tokens


# Create a mapping, sorted by total number of response words associated with each query word
@st.cache_data
def return_keyword_df(on, data):
    keyword_mapping = {}
    for idx, row in data.iterrows():
        # If stemming is on, apply stemming
        if on:
            query_words = tokenize(row['query_stemmed_words'])
            response_words = tokenize(row['response_stemmed_words'])
        else:
            query_words = tokenize(row["user_query"])
            response_words = tokenize(row["response"])
        for q_word in query_words:
            if q_word not in keyword_mapping:
                keyword_mapping[q_word] = Counter()
            keyword_mapping[q_word].update(response_words)

    # Convert the mapping to a DataFrame 
    keyword_df = pd.DataFrame(keyword_mapping).fillna(0).astype(int)
    row_sums = keyword_df.sum(axis=1)
    col_sums = keyword_df.sum(axis=0)

    # Sort rows and columns based on the sums
    keyword_df = keyword_df.loc[
        row_sums.sort_values(ascending=False).index,
        col_sums.sort_values(ascending=False).index,
    ]

    # Filter out all zero rows and columns
    keyword_df = keyword_df.loc[
        (keyword_df != 0).any(axis=1), (keyword_df != 0).any(axis=0)
    ]

    return keyword_df


def time_func(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' took {elapsed_time:.4f} seconds to complete.")
        return result
    return wrapper