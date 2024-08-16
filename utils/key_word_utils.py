from streamlit_agraph import agraph, Node, Edge, Config
import math

def draw_graph(option, select_word, keyword_df):
    nodes = []
    edges = []

    if option == "Query":
        num_nodes = sum(
            1 for word, count in keyword_df[select_word].items() if count > 0
        )
        angle_step = 2 * math.pi / num_nodes # Calculate the distance between each outer nodes
        radius = 300 # Change this to change the radius of the graph

        center_node_id = f"q_{select_word}"
        nodes.append(
            Node(
                id=center_node_id,
                label=select_word,
                size=25,
                color="#5db89d",
                font={"color": "#EEEEEE"},
            )
        )

        i = 0
        for word, count in keyword_df[select_word].items():
            if count > 0:
                angle = i * angle_step
                # Position of each new nodes calculated
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                nodes.append(
                    Node(
                        id=word,
                        label=word,
                        size=25,
                        font={"color": "#EEEEEE"},
                        color="#2c4857",
                        x=x,
                        y=y,
                    )
                )
                edges.append(
                    Edge(
                        source=center_node_id,
                        label=str(count),
                        target=word,
                        color="#5db89d",
                    )
                )
                i += 1
    elif option == "Response":
        center_node_id = f"r_{select_word}"
        nodes.append(
            Node(
                id=center_node_id,
                label=select_word,
                size=25,
                font={"color": "#EEEEEE"},
                color="#2c4857",
            )
        )

        num_nodes = sum(
            1 for word, count in keyword_df.loc[select_word].items() if count > 0
        )
        angle_step = 2 * math.pi / num_nodes
        radius = 300

        i = 0
        for word, count in keyword_df.loc[select_word].items():
            if count > 0:
                angle = i * angle_step
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                nodes.append(
                    Node(
                        id=word,
                        label=word,
                        size=25,
                        font={"color": "#EEEEEE"},
                        color="#5db89d",
                        x=x,
                        y=y,
                    )
                )
                edges.append(
                    Edge(
                        source=center_node_id,
                        label=str(count),
                        target=word,
                        color="#2c4857",
                    )
                )
                i += 1

    # Node graph configuration
    config = Config(
        width=1500,
        height=1000,
        directed=True,
        physics=False,
        hierarchical=False,
        # **kwargs
    )
    agraph(nodes=nodes, edges=edges, config=config)
