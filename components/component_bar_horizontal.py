from streamlit_elements import mui, nivo
from components.component_window import Window
from utils.common_utils import custom_theme


class Bar_Horizontal(Window.Item):
    def __init__(self, *args, data=None, title=None, keys=None, index=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data
        self.title = title
        self.keys = keys
        self.index = index

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
                        sx={
                            "fontFamily": "Roboto",
                            "fontWeight": "light",
                            "fontSize": 19,
                        },
                        children=self.title,
                    ),
                    sx={"flex": 1},
                )

            with mui.Box(sx={"flex": 1, "minHeight": 0}):
                nivo.Bar(
                    data=[
                        {
                            "word": word,
                            "count": count,
                        } for word, count in self.data.items()
                    ],
                    keys=["count"],
                    indexBy="word",
                    layout="horizontal",
                    margin={"top": 0, "right": 20, "bottom": 40, "left": 70},
                    padding=0.3,
                    valueScale={"type": "linear"},
                    indexScale={"type": "band", "round": True},
                    colors=["#5db89d"],
                    borderColor={"from": "color", "modifiers": [["darker", 1.6]]},
                    axisTop=None,
                    label={lambda d: ""},
                    enableGridY = False,
                    axisRight=None,
                    axisBottom={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legendPosition": "middle",
                        "legendOffset": 32,
                        "tickValues": 5
                    },
                    axisLeft={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legendPosition": "middle",
                        "legendOffset": -40
                    },
                    theme=custom_theme
                )