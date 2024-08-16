from streamlit_elements import mui, nivo
from components.component_window import Window
import pandas as pd
from utils.common_utils import custom_colors, custom_theme


class TimeRange(Window.Item):
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
                mui.icon.ViewTimeline()
                mui.Typography(self.title, sx={"flex": 1})
            with mui.Box(sx={"flex": 1, "minHeight": 0}):
                nivo.TimeRange(
                    data=self.convert_dataframe_to_list(self.dataframe),
                    emptyColor="#31363F",
                    colors=custom_colors,
                    margin={"top": 40, "right": 40, "bottom": 100, "left": 40},
                    dayBorderWidth=0,
                    dayBorderColor="#ffffff",
                    weekdayTicks=[0, 1, 2, 3, 4, 5, 6],
                    legends=[
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
                    theme=custom_theme,
                )
