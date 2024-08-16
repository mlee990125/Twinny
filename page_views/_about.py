import streamlit as st
from utils.data import get_data
from utils.common_utils import date_range_selector


data = get_data()
print("called in dashboard.py")

st.title("NarGo Query and Response Analysis")
expander = st.expander("Description")
expander.write(
    """
    This dashboard is a Queries and Responses analysis of the NarGo robot. NarGo is an Autonomous Mobile Robot (AMR) developed by  
    Twinny.ai and uses Speech To Text (STT) in order to create user requests (queries) to input into a Large Language Model (LLM).  
    NarGo uses NCSoft's LLM, VARCO to process user queries. Any interaction within the LLM is recorded to the Twinny database as logs.  
    From the Twinny database, the columns, "timestamp", "request", and "response" were used for analysis.
    
    Analysis includes:  
        - Query count by hour of the day, day of the week, and date visualized with various charts  
        - Unique response count and contents  
        - Key Word Analysis (with stemming) with node graph visualization   
        - Query and response classification  
        - Query and response similarities
    
    This app was built on streamlit and uses third-party components streamlit-elements, streamlit-agraph, and streamlit-aggrid.  
    The packages used for stemming and classification are KoNLPy and sentence-transformers. 
               
"""
)
github_repo_url = "https://github.ncsoft.com/varco-analytics/twinny-dashboard"
with expander:
    st.link_button("GitHub Repo", github_repo_url)
st.divider()

data = date_range_selector(data)

st.subheader("Selected Data")
st.write(data)
