import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from utils.data import get_data
from utils.common_utils import date_range_selector

st.title("Responses")

data = get_data()
data = date_range_selector(data)


# Group by identical user_query and calculate count of unique responses
response_consistency = data.groupby("user_query")["response"].nunique().reset_index()
response_consistency.columns = ["user_query", "unique_responses"]
response_consistency_sorted = response_consistency.sort_values(
    by="unique_responses", ascending=False
)


# Slider for rows displayed 
max_rows = response_consistency_sorted.shape[0]
if max_rows < 13:
    number_of_rows = max_rows
    if max_rows == 0:
        max_rows = 1
else:
    number_of_rows = 13

with st.sidebar:
    number_of_rows = st.slider(
        label=f"Select Number of Rows:",
        step=1,
        min_value=1,
        max_value=max_rows,
        value=number_of_rows,
    )


# Display the table
gb = GridOptionsBuilder.from_dataframe(response_consistency_sorted.head(number_of_rows))
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
gb.configure_selection(selection_mode="single", use_checkbox=True)
grid_options = gb.build()
grid_response = AgGrid(
    response_consistency_sorted.head(number_of_rows),
    gridOptions=grid_options,
    height=400,
    width="100%",
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
)


# Show unique responses when a cell is clicked
selected_row = grid_response["selected_rows"]

def find_responses(user_query_value):
    results = data.loc[data["user_query"] == user_query_value, "response"]
    return results.unique().tolist() if not results.empty else []

if selected_row is not None and len(selected_row) > 0:
    st.write(f"Unique Responses for the User Query: {selected_row['user_query'][0]}")
    st.write(find_responses(selected_row["user_query"][0]))
