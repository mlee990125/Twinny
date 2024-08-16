from streamlit_elements import mui, nivo
from components.component_window import Window
from utils.common_utils import custom_colors, custom_theme

class Pie(Window.Item):
    def __init__(self, *args, pie_data=None, title=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pie_data = pie_data
        self.title = title

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
                mui.Typography(self.title, sx={"flex": 1})
            with mui.Box(sx={"flex": 1, "minHeight": 0}):
                nivo.Pie(
                    data=self.pie_data,
                    margin={"top": 30, "right": 150, "bottom": 20, "left": 150},
                    innerRadius=0.65,
                    padAngle=2,
                    cornerRadius=3,
                    activeOuterRadiusOffset=8,
                    borderWidth=1,
                    colors=custom_colors,
                    borderColor={"from": "color", "modifiers": [["darker", 0.2]]},
                    arcLinkLabelsSkipAngle=10,
                    arcLinkLabelsTextColor="#EEEEEE",
                    arcLinkLabelsThickness=2,
                    arcLinkLabelsColor={"from": "color"},
                    arcLabelsSkipAngle=10,
                    arcLabelsTextColor="#EEEEEE",
                    arcLinkLabelsStraightLength = 5,
                    arcLinkLabelsDiagonalLength = 10,
                    enableArcLabels=False,
                    enableArcLinkLabels=True,
                    arcLabel = "id",
                    theme=custom_theme,
            
                )