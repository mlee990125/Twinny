from streamlit_elements import mui, nivo
from components.component_window import Window
from utils.common_utils import custom_theme, custom_colors


class Bar(Window.Item):
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
                        children="Query and Response Count by Day/Hour",
                    ),
                    sx={"flex": 1},
                )

            with mui.Box(sx={"flex": 1, "minHeight": 0}):
                nivo.Bar(
                    data=self.data,
                    keys=self.keys,
                    indexBy=self.index,
                    margin={"top": 50, "right": 130, "bottom": 50, "left": 60},
                    padding={0.3},
                    valueScale={"type": "linear"},
                    indexScale={"type": "band", "round": True},
                    colors=custom_colors,
                    borderColor={"from": "color", "modifiers": [["darker", 1.6]]},
                    axisTop=None,
                    axisRight=None,
                    axisBottom={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legendPosition": "middle",
                        "legendOffset": 32,
                        "truncateTickAt": 0
                    },
                    axisLeft={
                        "tickSize": 5,
                        "tickPadding": 5,
                        "tickRotation": 0,
                        "legendPosition": "middle",
                        "legendOffset": -40,
                        "truncateTickAt": 0,
                        "tickValues": 5,
                    },
                    labelSkipWidth=12,
                    labelSkipHeight=12,
                    labelTextColor={"from": "color", "modifiers": [["darker", 1.6]]},
                    label={lambda d: ""},
                    legends=[
                        {
                            "dataFrom": "keys",
                            "anchor": "bottom-right",
                            "direction": "column",
                            "justify": "false",
                            "translateX": 120,
                            "translateY": 0,
                            "itemsSpacing": 2,
                            "itemWidth": 100,
                            "itemHeight": 20,
                            "itemDirection": "left-to-right",
                            "itemOpacity": 0.85,
                            "symbolSize": 20,
                            "effects": [{"on": "hover", "style": {"itemOpacity": 1}}],
                        }
                    ],
                    theme=custom_theme,
                )
