from streamlit_elements import mui
from components.component_window import Window 

class Card(Window.Item):
    def __init__(self, *args, title, value, subtitle=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.value = value
        self.subtitle = subtitle

    def __call__(self):
        with mui.Paper(
            key=self._key,
            sx={
                "height": "100%",
                "display": "flex",
                "flexDirection": "column",
                "borderRadius": 2,
                "overflow": "hidden",
            },
            elevation=1,
        ):
            with self.title_bar():  
               pass
            
            with mui.Box(sx={"flex": 1, "p": 2, "display": "flex", "flexDirection": "column", "justifyContent": "center"}):
                mui.Typography(
                    self.value,
                    sx={
                        "fontSize": 70,
                        "fontWeight": "bold",
                        "fontFamily": "Roboto",
                    },
                    variant="h1",
                    component="div"
                )
                if self.subtitle:
                    mui.Typography(
                        self.subtitle,
                        sx={
                            "fontSize": 18,
                            "marginTop": 0,
                            "fontFamily": "Roboto",
                        },
                        
                    )

