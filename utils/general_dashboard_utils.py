import streamlit as st


@st.cache_data
def calculate_counts(data):
    hourly_counts = data["hour"].value_counts().sort_index().reset_index()
    hourly_counts.columns = ["hour", "user_query_count"]

    weekday_counts = (
        data["day_name"]
        .value_counts()
        .reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        .reset_index()
    )
    weekday_counts.columns = ["day_name", "user_query_count"]
    weekday_counts.fillna(0, inplace=True)

    data.set_index("timestamp", inplace=True)
    daily_queries = data["user_query"].resample("D").count().reset_index()
    daily_queries.columns = ["date", "user_query_count"]
    daily_queries["date"] = daily_queries["date"].dt.strftime("%Y-%m-%d")

    return hourly_counts, weekday_counts, daily_queries

@st.cache_data
def convert_dataframe_to_listof_dic(df):
    grouped_df = (
        df.groupby(["day_name", "hour", "day_of_week"])
        .size()
        .reset_index(name="user_query_count")
        .sort_values(["day_of_week", "hour"])
    )
    time_intervals = [
        ("09:00", "11:00"),
        ("11:00", "13:00"),
        ("13:00", "15:00"),
        ("15:00", "17:00"),
        ("17:00", "19:00"),
    ]

    def find_interval(hour):
        for start, end in time_intervals:
            if start <= hour < end:
                return f"{start} - {end}"
        return None

    grouped_df["interval"] = grouped_df["hour"].apply(find_interval)
    pivot_df = (
        grouped_df.pivot_table(
            index="day_name",
            columns="interval",
            values="user_query_count",
            aggfunc="sum",
        )
        .fillna(0)
        .reset_index()
    )
    result = pivot_df.to_dict("records")
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    sorted_data = sorted(result, key=lambda x: day_order.index(x["day_name"]))
    return sorted_data