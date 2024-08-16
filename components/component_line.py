from streamlit_elements import mui, nivo
from components.component_window import Window
import streamlit as st
from utils.common_utils import custom_theme
from datetime import datetime

st.markdown(
    """
    <style>
    @font-face {
        font-family: 'Poppins';
        src: url('/fonts/Poppins-Light.ttf') format('truetype');
        font-weight: 300;
        font-style: normal;
    }
    </style>
    """,
    unsafe_allow_html=True
)


class Line(Window.Item):
    def __init__(self, *args, data=None, title=None, tickvalues=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data
        self.title = title
        self.tickvalues = tickvalues

    def generate_monthly_ticks(self):
        # Assuming self.data contains data points with dates in x values
        dates = [point['x'] for series in self.data for point in series['data']]
        dates = sorted(set(dates))  # Get unique and sorted dates
        tick_values = []
        for date in dates:
            dt = datetime.strptime(date, "%Y-%m-%d")  # Adjust format as necessary
            if dt.day == 1:
                tick_values.append(date)
        return tick_values


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
                mui.Typography(
                    mui.Box(
                        component="span",
                        sx={"fontFamily": "'Poppins', sans-serif", "fontWeight": 1, "fontSize": 19},
                        children="Query and Response Count",
                    ),
                    sx={"flex": 1},
                )
            with mui.Box(sx={"flex": 1, "minHeight": 0}):
                nivo.Line(
                    data=self.data,
                    margin={"top": 40, "right": 70, "bottom": 40, "left": 70},
                    xScale={"type": "point"},
                    yScale={
                        "type": "linear",
                        "min": "auto",
                        "max": "auto",
                        "stacked": True,
                        "reverse": False,
                    },
                    yFormat=" >-.2f",
                    enablePoints=False,
                    enableGridX=False,
                    colors="#5db89d",
                    axisTop=None,
                    axisRight=None,
                    axisBottom={
                        "tickSize": 2,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        # "legend": "date",
                        "legendOffset": 36,
                        "legendPosition": "middle",
                        "truncateTickAt": 0,
                        "tickValues": self.generate_monthly_ticks(),
                    },
                    axisLeft={
                        "tickSize": 2,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        # "legend": "count",
                        "legendOffset": -40,
                        "legendPosition": "middle",
                        "truncateTickAt": 0,
                        "tickValues": 5,
                    },
                    pointSize=10,
                    pointColor={"theme": "background"},
                    pointBorderWidth=2,
                    pointBorderColor={"from": "serieColor"},
                    pointLabel="data.yFormatted",
                    pointLabelYOffset=-12,
                    enableTouchCrosshair=True,
                    useMesh=True,
                    # legends=[
                    #     {
                    #         "anchor": "bottom-right",
                    #         "direction": "column",
                    #         "justify": False,
                    #         "translateX": 100,
                    #         "translateY": 0,
                    #         "itemsSpacing": 0,
                    #         "itemDirection": "left-to-right",
                    #         "itemWidth": 80,
                    #         "itemHeight": 20,
                    #         "itemOpacity": 0.75,
                    #         "symbolSize": 12,
                    #         "symbolShape": "circle",
                    #         "symbolBorderColor": "rgba(0, 0, 0, .5)",
                    #         "effects": [
                    #             {
                    #                 "on": "hover",
                    #                 "style": {
                    #                     "itemBackground": "rgba(0, 0, 0, .03)",
                    #                     "itemOpacity": 1,
                    #                 },
                    #             }
                    #         ],
                    #     }
                    # ],
                    theme=custom_theme,
                )
