from streamlit_elements import mui
from components.component_window import Window
import base64


class Table(Window.Item):
    def __init__(self, *args, dataframe=None, title=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataframe = dataframe
        self.title = title

    def dataframe_to_columns_and_rows(self, df):
        columns = [
            {"field": col, "headerName": col.replace("_", " ").title(), "width": 150}
            for col in df.columns
        ]
        rows = []
        # columns.insert(0, {"field": "id", "headerName": "ID", "width": 90})
        for index, row in df.iterrows():
            row_data = {"id": index}  # Create an 'id' field starting from 1
            for col in df.columns:
                row_data[col] = (
                    round(row[col], 4) if isinstance(row[col], float) else row[col]
                )
            rows.append(row_data)

        return columns, rows

    def get_table_download_link(self):
        """Generates a link to download the table as a CSV file."""
        csv = self.dataframe.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f"data:file/csv;base64,{b64}"
        return href

    def __call__(self):
        columns, rows = self.dataframe_to_columns_and_rows(self.dataframe)
        with mui.Paper(
            key=self._key,
            sx={
                "display": "flex",
                "flexDirection": "column",
                "borderRadius": 3,
                "overflow": "hidden",
                "height": "100%"
            },
            elevation=1,
        ):
            with self.title_bar():
                # mui.icon.TableRows()  
                # mui.Typography(self.title, sx={"flex": 1})
                # # Add download button
                # with mui.Box(sx={"marginLeft": "auto"}):
                #     mui.Button(
                #         mui.icon.Download(),
                #         "Download CSV",
                #         component="a",
                #         href=self.get_table_download_link(),
                #         download=f"{self.title}.csv",
                #         sx={
                #             "color": "#EEEEEE",
                #             "textDecoration": "none",
                #             "fontSize": "0.75rem",
                #             "padding": "2px 8px",
                #             "minWidth": "0",
                #             "marginLeft": "8px",
                #         },
                #     )
                pass

            with mui.Box(sx={"flex": 1, "minHeight": 0, "width": "100%", "height": "calc(100% - 32px)"}):
                mui.DataGrid(
                    columns=columns,
                    rows=rows,
                    pageSize=12,
                    rowsPerPageOptions=[4],
                    checkboxSelection=False,
                    disableSelectionOnClick=True,
                    autoHeight=False,
                    disableExtendRowFullWidth=True
                )
