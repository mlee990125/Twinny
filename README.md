# Twinny Dashboard
### Clone project:
`git clone https://github.ncsoft.com/varco-analytics/twinny-dashboard.git`

### Dependencies Installation:  
`pip install -r dependencies.txt`

### Run app:
`streamlit run streamlit_app.py`

### About:
This dashboard provides an analysis of queries and responses for the NarGo robot, an Autonomous Mobile Robot (AMR) developed by Twinny.ai. NarGo uses Speech To Text (STT) to create user requests (queries) that are processed by NCSoft's Large Language Model (LLM), VARCO. Interactions within the LLM are recorded as logs in the Twinny database. This dashboard analyzes logs from the NarGo AMR at the National Science Museum (국립중앙과학관). The analysis utilizes the following columns from the database: "timestamp", "request", "response", "status" (including battery and location information), and "latency".

![User query to database visualization](/etc/image-20240314-083302.png)

### Analysis includes:  
- Query count by hour, day of the week, and date, visualized with various charts
- Unique response count and contents
- Key Word Analysis (with stemming) using node graph visualization
- Query and response classification
- Query and response similarities

### Dashboard Tabs
The dashboard is divided into five tabs, accessible through the sidebar:  
1. **General Dashboard**
    - Provides an overview of query and response counts within a specified time range, focusing on the museum's business hours (09:00 to 19:00). Includes various visualizations of query and response counts by date, day of the week, and hour.
2. **Queries and Responses**
    - Offers an in-depth look at the contents of the queries and responses. Clusters similar queries and responses to categorize them and displays the most common keywords after tokenizing the sentences.
3. **Key Word Search**
    - Visualizes the relationship between keywords using a node graph. Shows connections between query and response keywords, with edge weights indicating the frequency of keyword co-occurrences. Allows for individual keyword searches and stemming for further analysis.
4. **Model Evaluation**
    - Evaluates the VARCO model's performance in several areas:
        - **Response Coherence**: Assessed using cosine similarity between query and response embeddings.
        - **Lexical Diversity**: Measured by the Type-Token Ratio (TTR).
        - **Topic Modeling**: Identifies key topics within response texts using text preprocessing, Bag of Words Generation, and Latent Dirichlet Allocation Model.
        - **Response Consistency**: Analyzes the similarity of unique responses to a given query using cosine similarity on response embeddings.
5. **Upload New Data**
    - Allows for the upload of a CSV file to the SQL database. This process takes 2-3 minutes as it calculates query and response embeddings and stores them for faster retrieval when using the dashboard.

### Technology Stack
This app is built on Streamlit and utilizes the following third-party components: streamlit-elements, streamlit-agraph, streamlit-lottie, streamlit-folium, streamlit-extras, and streamlit-aggrid. The packages used for stemming and classification include KoNLPy and sentence-transformers, while scikit-learn and gensim are used for similarity computations and topic modeling.
