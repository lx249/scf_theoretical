# %%
import numpy as np
import pandas as pd
import networkx as nx
import yaml
import random

# Self-defined packages
from network import SCNetwork
from output import columns, Writer


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


# %% Calculate the amount of financing avaialble, i.e, max debt allowed.
def get_max_debt(cash, power):
    """
    Calculate the amount financing available, i.e., banking mandate limit.
    The minimum loan cap is 0 as negative loan cap is unreasonable.

    Parameters
    ----------
    `cash`: float
        The cash at current timestep.
    `power`: int 
        The power of the node. 
    """
    return max(cash * (power + 1), 0)


# %% Bank financing: return the amount of loan approaved
# Implementation 1: paper 
def get_loan(approach, **params): 
    """
    calculate the amount of loan a company is allowed to get.
    There are two ways to calculate: old and new.

    Parameters
    ----------
    `approach`: str
        The approach to calculate how much loan a company can get.
    `cash`: float
        The cash reserve at current timestep.
    `max_debt`: float
        The max allowed debt, i.e., the amount of banking financing available.
    `debt`: float
        The amount of debt at current timestep. 
    `ft`: float
        Financing threshold.

    Returns
    -------
        float: The allowed amount of loan.
    """

    def old(cash, max_debt, debt):
        allowed_loan = min(abs(cash), max_debt - debt)
        return max(0, allowed_loan)

    def new(cash, max_debt, debt, ft):
        return max(min(max_debt - debt, ft - cash), 0)

    cash = params["cash"]
    max_debt = params["max_debt"]
    debt = params["debt"]
    ft = params["ft"]
    
    if approach == "new":
        return new(cash, max_debt, debt, ft)
    else:
        return old(cash, max_debt, debt)

    
# %% Calculate interest needed to pay
def interest_to_pay(loan, annual_rate, borrow_period=120):
    return loan * annual_rate * (borrow_period / 365)


# %% Check if the node is illiuid and expects no profits
def is_bankrupt(cash_available, total_receiveable, total_payable):
    return cash_available <= 0 and total_receiveable < total_payable


# %% Select a financing threshold (ft).
def ft_forecast(costs, method="MA"):
    """
    Compute the financing threshold using moving cost average.

    Parameters
    ----------
    `costs`: list
        A list of cost at the past timestep
    `method`: str
        The name of time series forecasting method.
    """
    return sum(costs) / len(costs)
    

# %% Simulation configurations
network = SCNetwork(config_file="configs/network_config.yaml")

#Create the SC network
G = network.G

# Number of nodes
num_nodes = G.number_of_nodes()

# Simulation configurations
sim_config = load_config_file("configs/simulation_config.yaml")

t_max = sim_config["t_max"]
operation_fee = sim_config["operation_fee"]
loan_repayment_time = sim_config["loan_repayment_time"]
bank_annual_rate = sim_config["bank_annual_rate"]
invoice_annual_rate = sim_config["invoice_annual_rate"]
invoice_term = sim_config["invoice_term"]
window_size = sim_config["moving_average"]["window_size"]
powers = sim_config["powers"]

# Demand generator by normal distribution
distributions = sim_config["distributions"]
generator = sim_config["demand_generator"]
params = distributions[generator]



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
`receivables`, `payables`, `debts` and costs are sliding windows 
that update over the time step.
Note: `payables` include the debts. 
`cash_flow` records the cash movement between nodes, keyed by payment timestep.
"""
receivables = np.zeros((num_nodes, max_payment_delay+1))
payables = np.zeros((num_nodes, max_payment_delay+1)) 
debts = np.zeros((num_nodes, loan_repayment_time+1))
costs = np.zeros((num_nodes, window_size))
cash_flow = {}


"""
A dictionary stores new orders.
Its item {(buyer, seller): buy_amount, receive_amount, replenish_required} 
indicates: a `buyer` buy `buy_amount` from `seller`, 
received `receive_amount` require replenish or not.
"""
new_orders = {} 
total_demands = 0

# Define a writer for storing runtime data.
writer = Writer(sim_id=0)


# %% Iterate over time steps: t1 ... t_max.
for t in range(1, t_max + 1):
    demand = get_demand(generator, **params)
    total_demands += demand
    print("_"*30)
    print(f"[{t:<8}], demand: {demand}, total_demand: {total_demands}")

    # Save the data at current time step into file.
    output_at_t = {}
    for col in columns:
        output_at_t[col] = []

    # New demand from market: randomly select an OEM to fill the demand
    oem = select_seller(G, network.dummy_market)
    new_orders[(network.dummy_market, oem)] = (demand, 0, False)

    # Iterate all incoming orders, updapte receiveables, payables immediately, 
    # but deplay stock update till next time step (material needs one time step delivery).
    for (buyer, seller), (buy_amount, _, replenish_required) in new_orders.items():
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
        new_orders[(buyer, seller)] = (buy_amount, receive_amount, replenish_required) 
        
        
        """
        Action: update receivables and payables. 
                If buyer or seller is dummy node, then payment occurs immediately; 
                Otherwise, delay payment as much as possible, which is determined by a node's power.
        """
        # Pay for the order: immediately or delay
        payout = receive_amount * G.nodes[seller]["sell_price"]
        if buyer == network.dummy_market or seller == network.dummy_raw_material:  
            delay = 0
        else: # Delay
            p_b = G.nodes[buyer]["power"]
            p_s = G.nodes[seller]["power"]
            delay = payment_delay_matrix[p_b-1, p_s-1]
        payables[buyer][delay] += payout
        receivables[seller][delay] += payout


        # Record cash flow: moves from `buyer` to `seller` at timestep `k`
        if payout > 0:    
            k = t + delay # Keyed by actual payment timestep
            if k not in cash_flow:
                cash_flow[k] = {}
            cash_flow[k][(buyer, seller)] = payout


    """
    Action: handle receivables, payables, and debts at current time step. It includes:
            1) pay debt; 
            2) deduct operational fee; 
            3) receive receivables; 
            4) pay payables; and 
            5) decrement time to receive and pay
    """
    for node_idx in range(num_nodes):

        # Exclude bankrupt nodes
        _bankrupt = G.nodes[node_idx]["is_bankrupt"]
        if not _bankrupt:
            payout_today = (receivables[node_idx][0] 
                            - payables[node_idx][0]
                            - operation_fee)
            G.nodes[node_idx]["cash"] += payout_today

            # Record the costs at the timesteps within the given window size
            costs[node_idx][(t-1) % window_size] = abs(payout_today)

        _stock      = np.nan if _bankrupt else G.nodes[node_idx]["stock"]
        _cash       = np.nan if _bankrupt else G.nodes[node_idx]["cash"]
        _debt       = np.nan if _bankrupt else G.nodes[node_idx]["debt"]
        _unfilled   = np.nan if _bankrupt else G.nodes[node_idx]["unfilled"]
        _issued     = np.nan if _bankrupt else G.nodes[node_idx]["issued"]
        _received   = np.nan if _bankrupt else receivables[node_idx][0]
        _paid       = np.nan if _bankrupt else payables[node_idx][0]
        _b_loan     = np.nan if _bankrupt else 0

        output_at_t["timestep"].append(t)
        output_at_t["node_idx"].append(node_idx)
        output_at_t["tier"].append(G.nodes[node_idx]["tier"])
        output_at_t["power"].append(G.nodes[node_idx]["power"])
        output_at_t["is_bankrupt"].append(G.nodes[node_idx]["is_bankrupt"])
        
        output_at_t["stock"].append(_stock)
        output_at_t["cash"].append(_cash)
        output_at_t["order_from"].append(np.nan)
        output_at_t["buy_amount"].append(np.nan)
        output_at_t["receive_amount"].append(np.nan)
        output_at_t["purchase_value"].append(np.nan)
        output_at_t["sale_value"].append(np.nan)
        output_at_t["cash_from"].append(np.nan)
        output_at_t["pay_amount"].append(np.nan)
        output_at_t["unfilled"].append(_unfilled)
        output_at_t["issued"].append(_issued)
        output_at_t["b_loan"].append(_b_loan)
        output_at_t["receivable"].append(_received)
        output_at_t["payable"].append(_paid)
        output_at_t["debt"].append(_debt)


        # Decrement: the time to receive, to pay, and to repay decrement one time step.
        # After decrement, their values at current time step should be reset
        # to ZERO; we delay these actions after getting these values.
        for d in range(max_payment_delay-1):
            receivables[node_idx][d] = receivables[node_idx][d+1]
            payables[node_idx][d] = payables[node_idx][d+1]
        for d in range(loan_repayment_time-1):
            debts[node_idx][d] = debts[node_idx][d+1]
        receivables[node_idx][max_payment_delay] = 0
        payables[node_idx][max_payment_delay] = 0
        debts[node_idx][loan_repayment_time] = 0


    ### Updating for next timestep ###
    """
    Action: Selecting financing threshold (ft).
            Now, the threshold value is set as 0, which may introduce ML methods 
            to predict its value. The potential methods are: 
                1) moving average; 
                2) time series forecasting methods.
    """
    # To-Do: ft forecast using moving avareage


    """
    Action: Seek bank financing. 
            Check every node if they need bank financing. If so, then: 
                1) calculate the amount of loan they can secure;
                2) secure the loan, and add loan into their cash reserves;
                3) update payables, this loan plus it interest needs to pay after `bank_repayment_time`;
                4) check if the node is still bankrupt after financing, if so, 
                5) remove it from the network.
    """
    for node_idx in range(num_nodes):
        # Financing threshold forecasting using moving average
        ft = ft_forecast(costs[node_idx], "MA")
        node = G.nodes[node_idx]
        # Omit backrupt nodes
        if node["is_bankrupt"]: 
            continue
        """
        If cash is below financing threshold and debt is below loan cap, 
        then seek financing, apply for loan.
        """
        loan = 0
        cash_reserve = node["cash"]
        debt = node["debt"]
        max_debt = node["max_debt"]
        if cash_reserve <= ft:
            power = node["power"]
            loan = get_loan("new", 
                            cash=cash_reserve, 
                            max_debt=max_debt, 
                            debt=debt, 
                            ft=ft)
        
        interest = interest_to_pay(loan, bank_annual_rate, loan_repayment_time)
        loan_repayment = loan + interest
        debts[node_idx][loan_repayment_time-1] = loan_repayment
        
        payables[node_idx][loan_repayment_time-1] += loan_repayment
        G.nodes[node_idx]["cash"] += loan
        G.nodes[node_idx]["debt"] += loan_repayment
        # Output 
        output_at_t["cash"][node_idx] = G.nodes[node_idx]["cash"]
        output_at_t["debt"][node_idx] = G.nodes[node_idx]["debt"]
        output_at_t["b_loan"][node_idx] = loan

        # If cash is still not sufficient (<=0), then seek supply chain financing
        if G.nodes[node_idx]["cash"] <= 0: 
            deficit = abs(G.nodes[node_idx]["cash"])
            receive_early = min(receivables[node_idx][invoice_term], deficit)
            discount = interest_to_pay(receive_early,
                                       invoice_annual_rate,
                                       invoice_term)
            G.nodes[node_idx]["cash"] += (receive_early - discount)
            receivables[node_idx][invoice_term] -= receive_early
        # Update loan cap
        G.nodes[node_idx]["max_debt"] = get_max_debt(G.nodes[node_idx]["cash"], 
                                                     G.nodes[node_idx]["power"])
        total_receiveable = np.sum(receivables[node_idx, :])
        total_payable = np.sum(payables[node_idx, :])
        total_debt = np.sum(debts[node_idx, :])
        # Check if the node is bankrupt.
        # If so, remove its both in and out edges from the network
        if is_bankrupt(G.nodes[node_idx]["cash"], 
                       total_receiveable, 
                       total_payable):
            # Output: to terminal
            print(f"\n*WARNING*: Node {node_idx} is bankrupt!!!")
            print(f"Current cash: {cash_reserve}.")
            print(f"max debt: {max_debt}.")
            print(f"SC loan: {loan}.")
            # Output: to file
            output_at_t["is_bankrupt"][node_idx] = True
            G.nodes[node_idx]["is_bankrupt"] = True
            ebunch = list(G.in_edges(node_idx)) + list(G.out_edges(node_idx))
            G.remove_edges_from(ebunch)
            # network.draw()

    """
    Action: Update stock, unfilled_orders, issued_orders of both buyer and seller.
    """
    for (buyer, seller), (buy_amount, receive_amount, _) in new_orders.items():
        G.nodes[buyer]["stock"] += receive_amount
        G.nodes[seller]["stock"] -= receive_amount
        G.nodes[buyer]["unfilled"] -= receive_amount
        G.nodes[seller]["unfilled"] += (buy_amount - receive_amount)
        G.nodes[seller]["issued"] += receive_amount

        # Output: set the values of the remaining four columns
        output_at_t["order_from"][seller] = buyer
        output_at_t["buy_amount"][seller] = buy_amount
        output_at_t["receive_amount"][seller] = receive_amount
        _purchase_value = G.nodes[seller]["sell_price"] * receive_amount
        output_at_t["purchase_value"][buyer] = _purchase_value
        output_at_t["sale_value"][seller] = _purchase_value

    """
    Action: output cash flows at the current timestep to file.
    """
    if t in cash_flow:
        for (buyer, seller), pay_amount in cash_flow[t].items():
            output_at_t["cash_from"][seller] = buyer
            output_at_t["pay_amount"][seller] = pay_amount


    """
    Action: Update new orders, adding follow-up replenish orders.
    """
    replenish_orders = {}
    for (buyer, seller), (_, _, replenish_required) in new_orders.items():
        if replenish_required and not G.nodes[seller]["is_bankrupt"]:
            # Add follow-up replenish order
            new_seller = select_seller(G, seller)
            new_buyer = seller
            buy_amount = G.nodes[new_buyer]["unfilled"]
            replenish_orders[(new_buyer, new_seller)] = (buy_amount, 0, False)
    new_orders = replenish_orders
    
    # Write to file
    writer.append(output_at_t)

    # Check if the graph is still connected, i.e., if there is 
    # a path from dummy market to dummy raw material.
    # If so, proceed; otherwise, stop iteration.
    if not nx.has_path(G, network.dummy_raw_material,  network.dummy_market):
        print("\nNo path from dummy raw material to market!")
        print("Network is unconnected, simulation ends.")
        writer.write()
        break