import streamlit as st
from streamlit_elements import elements
from streamlit_lottie import st_lottie_spinner

from components.component_window import Window
from components.component_bar import Bar
from components.component_table import Table
from components.component_line import Line
from components.component_card import Card
from utils.common_utils import load_lottiefile, load_data
from utils.general_dashboard_utils import calculate_counts, convert_dataframe_to_listof_dic


# Custom CSS for styling
custom_css = """
    <style>
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
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
    # Dashboard overview expander
    with st.expander("Dashboard Overview"):
        st.write(
            """
            This dashboard provides a comprehensive overview of query and response counts within the specified time range, focusing on the museum's business hours from 09:00 to 19:00.
            All windows of the dashboard are draggable and resizable with mouse.

            ### Key Features:
            #### Query and Response Count (Line Chart):
            - Visualizes the daily number of queries and responses across the selected time range.

            #### Query and Response Count by Day/Hour (Bar Chart):
            - Displays the total number of queries and responses by day of the week and hour of the day.
            
            #### Customizable Date Range:
            - Use the date selector in the left sidebar to choose any dates within the dataset's time range for visualization.

            #### Table View Options:
            - Customize the data display using the "View Table by:" dropdown in the left sidebar. Options include:
                - Hour
                - Day of the Week
                - Date

            #### Average Values Toggle:
            - Enable the "Show Avg for Hour and Weekday" option in the left sidebar to display average values in the table instead of total counts.
            """
        )

    # Load and preprocess data
    data = load_data()
    if len(data) > 0:
        data["hour"] = data["timestamp"].dt.hour.apply(lambda x: f"{x:02d}:00")
        data["day_of_week"] = data["timestamp"].dt.dayofweek
        data["day_name"] = data["timestamp"].dt.day_name()

        # Calculate counts
        hourly_counts, weekday_counts, daily_queries = calculate_counts(data)
        
        # Sidebar options
        with st.sidebar:
            option = st.selectbox("View Table by: ", ("Hour", "Day of Week", "Date"))
            show_avg_hr_weekday = st.checkbox("Show Avg for Hour and Weekday")

        if show_avg_hr_weekday:
            weekday_counts["user_query_count"] /= len(daily_queries) / 7
            hourly_counts["user_query_count"] /= len(daily_queries)

        table_df = {
            "Hour": hourly_counts,
            "Day of Week": weekday_counts,
            "Date": daily_queries
        }[option]

        # Convert data for bar chart
        listof_dic = convert_dataframe_to_listof_dic(data)
        keys = ["09:00 - 11:00", "11:00 - 13:00", "13:00 - 15:00", "15:00 - 17:00", "17:00 - 19:00"]
        index = "day_name"

        # Prepare data for line chart
        line_data = [{"x": row["date"], "y": row["user_query_count"]} for _, row in daily_queries.iterrows()]
        tickvalues = [item["x"] for idx, item in enumerate(line_data) if idx % 31 == 0]

        # Create draggable elements
        with elements("general-dashboard"):
            board = Window()  

            bar_chart = Bar(
                board, 0, 3, 6, 3, data=listof_dic, 
                title="Query and Response Count by Day and Hour", keys=keys, index=index, minW=1, minH=1
                )
            
            table = Table(
                board, 9, 0, 3, 5, dataframe=table_df,
                title=f"Table by {option}", col1=table_df.columns[0], col2=table_df.columns[1], minW=1, minH=1
                )
            
            line_chart = Line(
                board, 0, 0, 9, 2, data=[{"id": "Total Queries", "data": line_data}],
                title="Query and Response Count Line", tickvalues=tickvalues, minW=1, minH=1
                )
            
            avg_q_and_r_card = Card(
                board, 6, 3, 3, 2,
                title="Avg Queries and Responses", value=f"{daily_queries['user_query_count'].mean().round(2)}",
                subtitle="Avg Queries and Responses", minW=1, minH=1
                )
            
            latency_card = Card(
                board, 6, 2, 3, 1,
                title="Latency Card", value=f"{int(data['latency'].mean())}ms",
                subtitle="Avg Response Latency", minW=1, minH=1
                )

            with board():
                bar_chart()
                table()
                line_chart()
                avg_q_and_r_card()
                latency_card()
    else:
        st.write("No Data Found")


with st_lottie_spinner(lottie_streamlit, height=800, key="loading"):
    main()
