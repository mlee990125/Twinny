from streamlit_elements import mui, nivo
from component_window import Window
import pandas as pd


class Calendar(Window.Item):
    def __init__(self, *args, dataframe=None, title=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataframe = dataframe
        self.title = title

    def convert_dataframe_to_list(self, df):
        df["date"] = pd.to_datetime(df["date"])
        result = []
        for index, row in df.iterrows():
            if row["user_query_count"] == 0:
                pass
            else:
                result.append(
                    {
                        "value": row["user_query_count"],
                        "day": row["date"].strftime("%Y-%m-%d"),
                    }
                )

        return result

    def __call__(self):
        data_list = self.convert_dataframe_to_list(self.dataframe)
        calendar_props = {
            "data": data_list,
            "from": data_list[0]["day"],
            "to": data_list[-1]["day"],
            "emptyColor": "#eeeeee",
            "minValue": "auto",
            "colors": ["#97e3d5", "#61cdbb", "#01D4B1"],
            "margin": {"top": 40, "right": 40, "bottom": 40, "left": 40},
            "yearSpacing": 40,
            "monthBorderColor": "#ffffff",
            "dayBorderWidth": 2,
            "dayBorderColor": "#ffffff",
            "legends": [
                {
                    "anchor": "bottom-left",
                    "direction": "row",
                    "justify": False,
                    "itemCount": 4,
                    "itemWidth": 42,
                    "itemHeight": 36,
                    "itemsSpacing": 14,
                    "itemDirection": "right-to-left",
                    "translateX": -30,
                    "translateY": -70,
                    "symbolSize": 20,
                }
            ],
        }
        with mui.Paper(
            key=self._key,
            sx={
                "display": "flex",
                "flexDirection": "column",
                "borderRadius": 3,
                "overflow": "hidden",
            },
            elevation=1,
        ):
            with self.title_bar():
                mui.icon.CalendarMonth()  
                mui.Typography(self.title, sx={"flex": 1})
            with mui.Box(sx={"flex": 1, "minHeight": 0}):
                nivo.Calendar(**calendar_props)
