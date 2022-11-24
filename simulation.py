# %%
import numpy as np
import networkx as nx
import yaml
import random
import time

# Self-defined packages
from network import SCNetwork


# %% Load config parameters
def load_config_file(config_file_path, mode="r"):
    with open(config_file_path, mode) as file:
        config = yaml.safe_load(file)
    return config


# %% Calculate node's supply likelihood
def supply_likelihood(graph, node_idx):
    power = graph.nodes[node_idx]["power"]
    return power * random.uniform(0, 1)


# %% Supplier selection: select a node with highest likelihood as the supplier
def select_seller(graph, buyer):
    sellers = list(graph.predecessors(buyer))
    num_sellers = len(sellers)
    if num_sellers == 0:
        return -1
    elif num_sellers == 1:
        return sellers[0]
    else:  # >= 1
        likelihoods = [ supply_likelihood(graph, s) for s in sellers ]
        return sellers[np.argmax(likelihoods)]


# %% Randomly generate positive, integer amount of demands.
def get_demand(distribution, **params):
    # Normal demand generator
    def normal(mean, sigma):
        d = int(np.random.normal(mean, sigma))
        return (d if d > 0 else get_demand(mean, sigma))

    # Poisson demand generator
    def poisson(lambda_value):
        return np.random.poisson(lambda_value)

    if distribution == "normal":
        mean = params["mean"]
        sigma = params["sigma"]
        return normal(mean, sigma)
    elif distribution == "poisson":
        lambda_value = params["lambda"]
        return poisson(lambda_value)
    else:
        raise ValueError(f"Unrecognised demand generator '{distribution}'!")


# %% Calculate the cap of available loan
def get_loan_cap(cash_reserve, power):
    return (power + 1) * cash_reserve


# %% Bank financing: return the amount of loan approaved
def get_loan(cash_reserve, loan_cap, debt):
    allowed_loan = min(abs(cash_reserve), loan_cap - debt - abs(cash_reserve))
    return max(0, allowed_loan)


# %% Calculate interest needed to pay
def interest_to_pay(loan, annual_rate, borrow_period=120):
    return loan * annual_rate * (365 / borrow_period)


# %% Check if the node is illiuid and expects no profits
def is_bankrupt(cash_available, total_receiveable, total_payable):
    return cash_available <= 0 and total_receiveable < total_payable


# %% Select a financing threshold
def select_financing_threshold():
    pass


# %% Simulation configurations
# Load the SC network
network = SCNetwork(config_file="configs/network_config.yaml")
G = network.G

# Number of nodes
num_nodes = G.number_of_nodes()

# Simulation configs
sim_config = load_config_file("configs/simulation_config.yaml")

t_max = sim_config["t_max"]
operation_fee = sim_config["operation_fee"]
loan_repayment_time = sim_config["loan_repayment_time"]
bank_annual_rate = sim_config["bank_annual_rate"]
window_size = sim_config["window_size"]

# Demand generator by normal distribution
demand_generator = sim_config["demand_generators"][0] 
distribution = demand_generator["distribution"]
params = demand_generator["params"]

powers = sim_config["powers"]


# %% Max payment delay
# Anonymous function to calculate payment delay 
# between a buyer with power p_b and a seller with power p_s
_delay = lambda p_b, p_s: max(30 * (p_b - p_s) + 60, 30)

num_powers = len(powers)
payment_delay_matrix = np.zeros((num_powers, num_powers), dtype=int)
(rows, cols) = payment_delay_matrix.shape
for i in range(rows):
    for j in range(cols):
        payment_delay_matrix[i, j] = _delay(i + 1, j + 1)
max_payment_delay = payment_delay_matrix.max()


"""
Receivable, payable cash, and debts until repayment time
`receivables`, `payables`, and `debts` are sliding windows 
that update over the time step.
"""
receivables = np.zeros((num_nodes, max_payment_delay+1))
payables = np.zeros((num_nodes, max_payment_delay+1))
debts = np.zeros((num_nodes, loan_repayment_time+1))


"""
A dictionary stores new orders.
Its item {(buyer, seller): buy_amount, replenish_required} 
indicates: a `buyer` buy `buy_amount` from `seller`, require replenish or not.
"""
new_orders = {} 
total_demands = 0


%time
# %% Iterate over time steps: t1 ... t_max.
for t in range(1, t_max + 1):
    demand = get_demand(distribution, **params)
    total_demands += demand
    print("_"*30)
    print(f"[{t:<8}], demand: {demand}, total_demand: {total_demands}")
    
    # New demand from market: randomly select an OEM to fill the demand
    oem = select_seller(G, network.dummy_market)
    new_orders[(network.dummy_market, oem)] = (demand, False)

    # Iterate all incoming orders, updapte stock, receiveables, payables accordingly.
    for (buyer, seller), (buy_amount, replenish_required) in new_orders.items():
        """
        Action: stock balancing without check cash reserve.
                `buy_amount`: the accumulated amount of its unfilled orders;
                `receive_amount`: the actual receive amount, which is constrained by 
                the seller's stock.
        """
        stock = G.nodes[seller]["stock"]
        receive_amount = min(stock, buy_amount)
        print(f"  ({buyer:>2}->{seller:>2}): buy {buy_amount}, receive {receive_amount}")

        # Label if the order triggers replenishment
        replenish_required = True if stock <= buy_amount else False
        new_orders[(buyer, seller)] = (buy_amount, replenish_required) 
        
        # Update stock, unfilled_orders of both buyer and seller
        G.nodes[buyer]["stock"] += receive_amount
        G.nodes[seller]["stock"] -= receive_amount
        G.nodes[buyer]["unfilled"] -= receive_amount
        G.nodes[seller]["unfilled"] += (buy_amount - receive_amount)

        """
        Action: update receivables and payables. 
                If buyer or seller is dummy node, then payment occurs immediately; 
                Otherwise, delay payment as much as possible, which is determined by a node's power
        """
        payout = receive_amount * G.nodes[seller]["sell_price"]
        # Pay immediately
        if buyer == network.dummy_market or seller == network.dummy_raw_material:  
            G.nodes[buyer]["cash"] -= payout
            G.nodes[seller]["cash"] += payout
        # Delay payment
        else: 
            p_b = G.nodes[buyer]["power"]
            p_s = G.nodes[seller]["power"]
            delay = payment_delay_matrix[p_b - 1, p_s - 1]
            payables[buyer][delay] += payout
            receivables[seller][delay] += payout
           
    
    """
    Action: handle receivables, payables, and debts at current time step. It includes:
            1) pay debt; 
            2) deduct operational fee; 
            3) receive receivables; 
            4) pay payables; and 
            5) decrement time to receive and pay
    """
    for node_idx in range(0, num_nodes):
        if G.nodes[node_idx]["is_bankrupt"]: 
            continue
        debt_to_pay = debts[node_idx][0]  # Including interest
        payout_today = (receivables[node_idx][0] 
                  - payables[node_idx][0] 
                  - operation_fee 
                  - debt_to_pay)
        G.nodes[node_idx]["cash"] += payout_today

        # Decrement: the time to receive and pay decrements
        d = 0 
        while d <= (max_payment_delay - 1):
            receivables[node_idx][d] = receivables[node_idx][d+1]
            payables[node_idx][d] = payables[node_idx][d+1]
            debts[node_idx][d] = debts[node_idx][d+1]
            d = d + 1
        receivables[node_idx][d] = 0
        payables[node_idx][d] = 0
        debts[node_idx][d] = 0
        
    
        
    """
    Action: Update new orders, adding follow-up replenish orders.
    """
    replenish_orders = {}
    for (buyer, seller), (_, replenish_required) in new_orders.items():
        if replenish_required:
            # Add follow-up replenish order
            new_seller = select_seller(G, seller)
            new_buyer = seller
            buy_amount = G.nodes[new_buyer]["unfilled"]
            replenish_orders[(new_buyer, new_seller)] = (buy_amount, False)
    new_orders = replenish_orders

    """
    Action: Selecting financing threshold.
            Now, the threshold value is set as 0, which may introduce ML methods 
            to predict its value. The potential methods are: 
                1) moving average; 
                2) time series forecasting methods.
    """
    financing_threshold = 0


    """
    Action: Seek financing (loan). Check every node if they need bank financing. 
            If so, then: 
                1) calculate the amount of loan they can secure;
                2) secure the loan, and add loan into their cash reserves;
                3) update payables, this loan plus it interest needs to pay after `bank_repayment_time`;
                4) check if the node is still bankrupt after financing, if so, 
                5) remove it from the network.
    """
    bankrupt_nodes = []
    for node_idx in range(0, num_nodes):
        node = G.nodes[node_idx]
        # Omit backrupt nodes
        if node["is_bankrupt"]: 
            continue
        cash_reserve = node["cash"]
        loan = 0
        # If cash is below financing threshold, seek financing, get the loan it can secure
        if cash_reserve <= financing_threshold:
            power = node["power"]
            debt = node["debt"]
            loan_cap = get_loan_cap(cash_reserve, power)
            loan = get_loan(cash_reserve, loan_cap, debt)

        interest = interest_to_pay(loan, bank_annual_rate, loan_repayment_time)
        loan_repayment = loan + interest
        debts[node_idx][loan_repayment_time-1] = loan_repayment
        payables[node_idx][loan_repayment_time-1] += loan_repayment
        G.nodes[node_idx]["cash"] += loan
        G.nodes[node_idx]["debt"] += loan_repayment

        # Check if the node is bankrupt. 
        # If so, remove its both in and out edges from the network
        total_receiveable = np.sum(receivables[node_idx, :])
        total_payable = np.sum(payables[node_idx, :])
        if is_bankrupt(cash_reserve + loan, total_receiveable, total_payable):
            print(f"\n*WARNING*: Node {node} is bankrupt!!!")
            ebunch = list(G.in_edges(node)) + list(G.out_edges(node))
            G.remove_edges_from(ebunch)
            G.nodes[node_idx]["is_bankrupt"] = True
            network.draw()


    # Check if the graph is still connected, i.e., if there is 
    # a path from dummy market to dummy raw material.
    # If so, proceed; otherwise, break
    if not nx.has_path(G, network.dummy_raw_material,  network.dummy_market):
        print("\nNo path from dummy raw material to market!")
        break

# To-Do: deal with bankcrupt nodes