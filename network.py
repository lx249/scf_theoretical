# %% 
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import yaml
import sys


# %% Load graph config parameters
def _load_config_file(config_file_path, mode="r"):
    with open(config_file_path, mode) as file:
        config = yaml.safe_load(file)
    return config


# %% Get data
def _get_data(edges_file, nodes_file):
    edges_df = pd.read_csv(edges_file, header=0, index_col=False)
    nodes_df = pd.read_csv(nodes_file, header=0, index_col=False)
    return edges_df, nodes_df


# %%Create graph
def _create_graph(edges):
    G = nx.from_pandas_edgelist(edges, 
                                source="start", target="end", 
                                create_using=nx.DiGraph())
    return G


# %% Calculate the tiers.
# key: tier index, value: the list of nodes at this tier.
def _calc_tiers(graph, source_node=0):
    tiers = {}
    node_depths = nx.shortest_path_length(graph, source_node)
    sorted_node_depths = dict(sorted(node_depths.items(), key=lambda x: x[0]))
    for k, v in sorted_node_depths.items():
        if v not in tiers.keys():
            tiers[v] = {}
            tiers[v]["width"] = 1
            tiers[v]["nodes"] = [k]
        else:
            tiers[v]["width"] += 1
            tiers[v]["nodes"].append(k)
    return sorted_node_depths, tiers


# %% Get info about the shape of tiers
def _shape_of_tiers(tiers):
    values = list(tiers.values())
    max_tier_width = max([item["width"] for item in values])
    num_of_tiers = len(values)
    return max_tier_width, num_of_tiers


# %% Determine a node' power, i.e., a firm's bargaining power
def _node_power(homogenity, tier_width, min_tier_width=2):
    if homogenity:
        power = 1  # All node gets same bargaining power
    else:
        power = random.uniform(0, 1) * (min_tier_width / tier_width)
    return int(power // (1 / 3) + 1)


# %% Calculate node position.
# The entire drawing area is spanning from bottom left (0, 0) (origin point)
# to top right (1, 1)
def _tiered_layout(tiers, max_tier_width, num_tiers, padding_x=0.1, padding_y=0.1):
    left_x, right_x = padding_x, 1 - padding_x
    bottom_y, top_y = padding_y, 1 - padding_y
    canvas_width, canvas_length = right_x - left_x, top_y - bottom_y

    # Horizontally position nodes from right to left tier by tier
    # Vertically position nodes in central area with even interval
    node_pos = {}
    y_intv = canvas_width / (max_tier_width - 1)
    linspace_x = np.linspace(left_x, right_x, num_tiers)
    for tier_idx, v in tiers.items():
        tier_width = tiers[tier_idx]["width"]
        base_y = top_y - (max_tier_width - tier_width) * y_intv / 2  # Most top node
        nodes = tiers[tier_idx]["nodes"]
        for idx, v in enumerate(nodes):
            x_pos = linspace_x[num_tiers - tier_idx - 1]
            y_pos = base_y - idx * y_intv
            node_pos[v] = (x_pos, y_pos)
    return node_pos


# %% Draw graph
def _draw_graph(graph, node_pos, figsize=(8, 4), **options):
    plt.figure(figsize=figsize)
    nx.draw_networkx(graph, pos=node_pos, **options)
    nx.draw_networkx(graph, pos=node_pos, 
                     edge_lebels={(0, 2)): "50"},
                     font_color="red")


# %% Supply chain network
class SCNetwork(object):

    def __init__(self, config_file):
        config = _load_config_file(config_file)
        topology = config["topology"]
        homogenity = config["homogenity"]
        edges_file = config["edges_file"].format(topology=topology)
        nodes_file  = config["nodes_file"].format(topology=topology)
        edges_df, nodes_df = _get_data(edges_file, nodes_file)
        
        # Create graph and initialise nodes
        G = _create_graph(edges_df)
        node_depths, tiers = _calc_tiers(G)
        max_tier_width, num_tiers = _shape_of_tiers(tiers)

        attrs = {}  
        for _, row in nodes_df.iterrows():
            node_idx = row["node_idx"]
            tier_no = node_depths[node_idx]
            attrs[node_idx] = {
                                "buy_price": row["buy_price"], 
                                "sell_price": row["sell_price"],
                                "cash": row["cash"],
                                "tier": tier_no,
                                "power": _node_power(homogenity, tiers[tier_no]["width"], 2),
                              }
        
        nx.set_node_attributes(G, attrs)
        nx.set_node_attributes(G, 0, "stock") 
        nx.set_node_attributes(G, 0, "unfilled")
        nx.set_node_attributes(G, 0, "issued")
        nx.set_node_attributes(G, 0, "debt")
        nx.set_node_attributes(G, False, "is_bankrupt")

        dummy_raw_material = 0 # Dummy raw material node has infinite stock
        dummy_market = 19  # Dummy market has infinite cash
        nx.set_node_attributes(G, {dummy_market: {"cash": sys.maxsize, "power": -1}})
        nx.set_node_attributes(G, {dummy_raw_material: {"stock": sys.maxsize, "power": -1}})

        # Initialisation
        self.G = G
        self.dummy_raw_material = dummy_raw_material
        self.dummy_market = dummy_market
        self.config = config
        self.node_depths = node_depths
        self.tiers = tiers
        self.num_tiers = num_tiers
        self.max_tier_width = max_tier_width

    
    def draw(self):
        graph_options = self.config["graph_options"]
        node_pos = _tiered_layout(self.tiers, self.max_tier_width, self.num_tiers)
        _draw_graph(self.G, node_pos, **graph_options)


    
    
