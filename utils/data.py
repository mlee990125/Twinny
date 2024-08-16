import pandas as pd
import json
import numpy as np
import time
import streamlit as st
from aidp_connector.db.mysql_manager import MysqlExecuteManager
from konlpy.tag import Okt, Kkma, Hannanum
from sentence_transformers import SentenceTransformer


VR_DB_AUTH = {
    "host": "10.246.15.75",
    "port": 62222,
    "db_name": "twinnydb",
    "db_user": "twinnyuser",
    "db_pw": "twinny123",
}


class ReportData:
    def __init__(self):
        try:
            self.manager = MysqlExecuteManager(VR_DB_AUTH)
        except:
            raise Exception("Invalid authentication for DB")

    def send_query(self, query):
        return pd.DataFrame(self.manager.fetch_to_df(query))


vrd = ReportData()
okt = Okt()
kkma = Kkma()
hannanum = Hannanum()

@st.cache_resource
def get_model(filepath):
    return SentenceTransformer(filepath)

model = get_model("/home/ubuntu/KR-SBERT-Medium-klueNLItriplet_PARpair-klueSTS")

def stem_word(word):
    # Try Okt first
    stemmed = okt.nouns(word)
    
    # If Kkma returns empty, try Hannanum
    if not stemmed:
        stemmed = hannanum.nouns(word)
    
    # If all stemmers return empty, use the original word
    return stemmed if stemmed else [word]


def stem_words(text):
    if not isinstance(text, str):
        return ''
    words = text.split()
    stemmed = []
    for word in words:
        stemmed.extend(stem_word(word))
    return ' '.join(stemmed)

def clean_json_string(json_str):
    if not isinstance(json_str, str):
        return json_str
    
    try:
        # Parse the JSON string
        data = json.loads(json_str)
        
        # Function to recursively replace NaN with None
        def replace_nan(item):
            if isinstance(item, dict):
                return {k: replace_nan(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [replace_nan(i) for i in item]
            elif isinstance(item, float) and np.isnan(item):
                return None
            else:
                return item
        
        # Clean the data
        cleaned_data = replace_nan(data)
        
        # Convert back to JSON string
        return json.dumps(cleaned_data)
    except json.JSONDecodeError:
        # If it's not valid JSON, return it as is
        return json_str

def process_chunk(chunk, vrd):
    start_time = time.time()
    # Clean and preprocess the chunk
    if 'status' in chunk.columns:
        chunk['status'] = chunk['status'].apply(clean_json_string)
    chunk['user_query'] = chunk['user_query'].fillna('')
    chunk['response'] = chunk['response'].fillna('')
    
    # Stem words if 'stemmed_words' column doesn't exist or is empty
    if 'query_stemmed_words' not in chunk.columns:
        chunk['query_stemmed_words'] = ''
    chunk.loc[chunk['query_stemmed_words'].isnull() | (chunk['query_stemmed_words'] == ''), 'query_stemmed_words'] = \
        chunk.loc[chunk['query_stemmed_words'].isnull() | (chunk['query_stemmed_words'] == ''), 'user_query'].apply(stem_words)
    
    if 'response_stemmed_words' not in chunk.columns:
        chunk['response_stemmed_words'] = ''
    chunk.loc[chunk['response_stemmed_words'].isnull() | (chunk['response_stemmed_words'] == ''), 'response_stemmed_words'] = \
        chunk.loc[chunk['response_stemmed_words'].isnull() | (chunk['response_stemmed_words'] == ''), 'response'].apply(stem_words)
    
    # Calculate embeddings
    query_embeddings = model.encode(chunk['user_query'].tolist())
    response_embeddings = model.encode(chunk['response'].tolist())
    
    # Convert embeddings to binary for storage
    chunk['query_embedding'] = [embedding.tobytes() for embedding in query_embeddings]
    chunk['response_embedding'] = [embedding.tobytes() for embedding in response_embeddings]
    
    columns = ['timestamp', 'user_query', 'response', 'query_stemmed_words', 'response_stemmed_words', 'query_embedding', 'response_embedding']
    if 'status' in chunk.columns:
        columns.append('status')
    if 'latency' in chunk.columns:
        columns.append('latency')
    
    insert_query = f"""
    INSERT INTO twinnydb.interactions_all 
    ({', '.join(columns)}) 
    VALUES ({', '.join(['%s'] * len(columns))})
    ON DUPLICATE KEY UPDATE 
    {', '.join([f"{col} = VALUES({col})" for col in columns if col not in ['timestamp']])};
    """
    
    data_to_insert = chunk[columns].values.tolist()

    try:
        vrd.manager.write_list_to_db(query=insert_query, data=data_to_insert)
        st.write(f"Inserted/Updated {len(chunk)} rows successfully.")
    except Exception as e:
        st.write(f"An error occurred during insertion: {e}")
    
    end_time = time.time()
    st.session_state.chunk_counter += 1
    st.write(f"Function process_chunk (chunk {st.session_state.chunk_counter}) {end_time - start_time:.4f} seconds to execute.")
    
def clear_table():
    insert_query = """
    TRUNCATE TABLE twinnydb.interactions_all;
    """
    vrd.send_query(insert_query)

@st.cache_data
def get_data():
    print('called in get_data')
    a = vrd.send_query("select * from twinnydb.interactions_all")
    data = pd.DataFrame(a)
    data["timestamp"] = data["timestamp"] + pd.Timedelta(hours=9)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data = data.sort_values(by="timestamp")

    data['user_query'] = data['user_query'].str.replace('sp', '네')
    data['response'] = data['response'].str.replace('sp', '네')

    data['query_embedding'] = data['query_embedding'].apply(lambda x: np.frombuffer(x, dtype=np.float32))
    data['response_embedding'] = data['response_embedding'].apply(lambda x: np.frombuffer(x, dtype=np.float32))

    return data






