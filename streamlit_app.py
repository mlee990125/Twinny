import streamlit as st

general_dashboard_page = st.Page("page_views/p1_general_dashboard.py", title="General Dashboard", icon=":material/dashboard:")
q_and_r_page = st.Page("page_views/p2_queries_and_responses.py", title="Queries and Responses", icon=":material/chat:")
key_word_page = st.Page("page_views/p3_key_words.py", title="Key Word Search", icon=":material/search:")
evaluate_page = st.Page("page_views/p4_evaluate.py", title="Model evaluation", icon=":material/check:")
upload_page = st.Page("page_views/p5_upload_new_data.py", title="Upload New Data", icon=":material/upload:")

pg = st.navigation([general_dashboard_page, q_and_r_page, key_word_page, evaluate_page, upload_page])
st.set_page_config(page_title="Twinny Dashboard", layout="wide") #initial_sidebar_state="collapsed"
pg.run()


#Color values:
#222831
#2c4857
#2e6c79
#399291
#5db89d