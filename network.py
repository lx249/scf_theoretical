"""
Create a supply chain network using `networkx` package.
Author: Liming Xu
Email: lx249@cam.ac.uk
"""

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
    tier_widths_dummies_excluded = [item["width"] for item in values][1:-1]
    num_of_tiers = len(values)
    max_tier_width = max(tier_widths_dummies_excluded)
    min_tier_width  = min(tier_widths_dummies_excluded)
    return max_tier_width, min_tier_width, num_of_tiers


# %% Determine a node' power, i.e., a firm's bargaining power
def _node_power(homogeneous, 
                tier_width, 
                min_tier_width=2):
    if homogeneous:
        power = 1  # All node gets small powers
    else:
        x = random.uniform(0, 1) * (min_tier_width / tier_width)
        power = int(x // (1 / 3) + 1)
    return power


# %% Calculate node position.
# The entire drawing area is spanning from bottom left (0, 0) (origin point)
# to top right (1, 1)
def _tiered_layout(tiers, 
                   max_tier_width, num_tiers, 
                   padding_x=0.1, padding_y=0.1):
    left_x, right_x = padding_x, 1 - padding_x
    bottom_y, top_y = padding_y, 1 - padding_y
    canvas_width, canvas_length = right_x - left_x, top_y - bottom_y

    # Horizontally position nodes from right to left tier by tier
    # Vertically position nodes in central area with even interval
    layout = {}
    y_intv = canvas_width / (max_tier_width - 1)
    linspace_x = np.linspace(left_x, right_x, num_tiers)
    for tier_idx, v in tiers.items():
        tier_width = tiers[tier_idx]["width"]
        base_y = top_y - (max_tier_width - tier_width) * y_intv / 2  # Most top node
        nodes = tiers[tier_idx]["nodes"]
        for idx, v in enumerate(nodes):
            x_pos = linspace_x[num_tiers - tier_idx - 1]
            y_pos = base_y - idx * y_intv
            layout[v] = (x_pos, y_pos)
    return layout



# %% Supply chain network
class SCNetwork(object):

    def __init__(self, 
                 topology, homogeneous, 
                 powers, market_shares, 
                 config_file):
        config = _load_config_file(config_file)
        edges_file = config["edges_file"].format(topology=topology)
        nodes_file  = config["nodes_file"].format(topology=topology)
        edges_df, nodes_df = _get_data(edges_file, nodes_file)
        
        # Create graph and initialise nodes
        G = _create_graph(edges_df)
        node_depths, tiers = _calc_tiers(G)
        max_tier_width, min_tier_width, num_tiers = _shape_of_tiers(tiers)
        layout = _tiered_layout(tiers, max_tier_width, num_tiers)
        

        attrs = {}  
        for _, row in nodes_df.iterrows():
            node_idx = row["node_idx"]
            tier_no = node_depths[node_idx]
            power = _node_power(homogeneous, 
                                tiers[tier_no]["width"], 
                                min_tier_width)
            
            attrs[node_idx] = {
                                "buy_price": row["buy_price"], 
                                "sell_price": row["sell_price"],
                                "cash": row["cash"],
                                "tier": tier_no,
                                "power": power,
                                "market_share": market_shares[power-1],
                                "max_debt": (power+1) * row["cash"],
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
        self.layout = layout
        self.node_colors = self._get_node_colors(config["node_options"])
        self.node_labels = self._get_node_labels(config["node_options"])

    # %% Get the node labels


    def _get_node_labels(self, node_options):
        labels = {}
        for node_idx in range(self.G.number_of_nodes()):
            labels[node_idx] = str(node_idx)
        labels[self.dummy_raw_material] = ""
        labels[self.dummy_market] = ""
        return labels


    # %% Get the node colors
    def _get_node_colors(self, node_options):
        _color = node_options["healthy"]["color"]
        colors = [_color] * self.G.number_of_nodes()
        colors[self.dummy_raw_material] = node_options["raw_material"]["color"]
        colors[self.dummy_market] = node_options["market"]["color"]
        return colors


    # %% Draw graph and return current figure and axes
    def _draw_graph(self, figsize=(10, 4), **options):
        plt.figure(figsize=figsize, frameon=False)
        nx.draw_networkx(self.G, 
                         pos=self.layout,
                         labels=self.node_labels,
                         node_color=self.node_colors,
                         **options)
        return (plt.gcf(), plt.gca())


    def draw(self):
        graph_options = self.config["graph_options"]
        fig, ax = self._draw_graph(self.config["figsize"], **graph_options)
        return fig, ax





    
    
