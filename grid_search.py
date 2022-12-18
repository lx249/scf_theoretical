"""
Runing simulation by using different combinations of input parameters.
Author: Liming Xu
Email: lx249@cam.ac.uk
"""

# %% 
import itertools 
import numpy as np
from simulation import SCFSimulation
from utils import load_config_file


def simconfig_generator(input_params):
    """
    Enumerate input parameters for grid search.
    """
    # Part one - basics
    t_max                    = input_params["t_max"]
    lst_topology             = input_params["network_topology"]
    lst_homogeneous          = input_params["homogeneous"]
    lst_operation_fee        = input_params["operation_fee"]

    # Part two - demand generation 
    lst_demand_distribution  = input_params["demand_distribution"]
    demand_distribution      = lst_demand_distribution[0]
    lst_demand_mean          = input_params["distribution_params"][demand_distribution]["mean"]
    lst_demand_sigma         = input_params["distribution_params"][demand_distribution]["sigma"]

    # Part three - company power and marker shares
    powers                   = input_params["powers"]
    lst_small_market_shares  = [ 1 ]
    lst_medium_market_shares = input_params["market_shares"]["medium"]
    lst_large_market_shares  = input_params["market_shares"]["large"]
    
    # Part four - financing 
    lst_financed             = input_params["financed"]
    lst_loan_repayment_time  = input_params["loan_repayment_time"]
    lst_bank_annual_rate     = input_params["bank_annual_rate"]
    lst_invoice_annual_rate  = input_params["invoice_annual_rate"]
    lst_invoice_term         = input_params["invoice_term"]

    # Part five - financing threshold
    lst_paradigm             = input_params["paradigm"]
    lst_ma_window_size       = input_params["moving_average"]["window_size"]

    # Input parameter enumeration
    basics = itertools.product(
        lst_topology, 
        lst_homogeneous, 
        lst_operation_fee)

    demand_generation = itertools.product( 
        lst_demand_distribution, 
        lst_demand_mean, 
        lst_demand_sigma)
    
    all_market_share_combs = itertools.product(
        lst_small_market_shares,
        lst_medium_market_shares,
        lst_large_market_shares)
    market_shares = [(s, m, l) 
                     for s, m, l in all_market_share_combs
                     if s <= m and m <= l]

    financing_params = itertools.product(
        lst_loan_repayment_time,
        lst_bank_annual_rate,
        lst_invoice_annual_rate,
        lst_invoice_term
    )

    financing = [(False, 0, 0, 0, 0)]  # 0 as a placeholder
    for p1, p2, p3, p4 in financing_params:
        financing.append((True, p1, p2, p3, p4))

    financing_threshold = [("reactive", 1)]  # 1 as a placeholder
    for ws in lst_ma_window_size:
        financing_threshold.append(("proactive", ws))
    
    sim_configs = []
    sim_id = 0
    for v1, v2, v3, v4, v5 in itertools.product(
        basics,
        demand_generation,
        market_shares,
        tuple(financing),
        tuple(financing_threshold)
    ): 
        sim_id += 1
        sim_config = {}
        sim_config["sim_id"] = sim_id
        sim_config["t_max"] = t_max
        sim_config["network_topology"] = v1[0]
        sim_config["homogeneous"] = v1[1]
        sim_config["operation_fee"] = v1[2]

        sim_config["demand_distribution"] = v2[0]
        sim_config["distribution_params"] = {"mean": v2[1], "sigma": v2[2]}

        sim_config["financed"] = v4[0]
        sim_config["loan_repayment_time"] = v4[1]
        sim_config["bank_annual_rate"] = v4[2]
        sim_config["invoice_annual_rate"] = v4[3]
        sim_config["invoice_term"] = v4[4]
        sim_config["paradigm"] = v5[0]
        sim_config["window_size"] = v5[1]
        sim_config["powers"] = powers
        sim_config["market_shares"] = v3

        sim_configs.append(sim_config)
    
    return sim_configs


def single_run_params(sim_config):
    """
    Generate the parameters for a signle simulation running.
    """
    sim_id              = sim_config["sim_id"]
    topology            = sim_config["network_topology"]
    homogeneous         = sim_config["homogeneous"]
    t_max               = sim_config["t_max"]
    financed            = sim_config["financed"]
    paradigm            = sim_config["paradigm"]
    operation_fee       = sim_config["operation_fee"]
    loan_repayment_time = sim_config["loan_repayment_time"]
    bank_annual_rate    = sim_config["bank_annual_rate"]
    invoice_annual_rate = sim_config["invoice_annual_rate"]
    invoice_term        = sim_config["invoice_term"]
    window_size         = sim_config["moving_average"]["window_size"]
    powers              = sim_config["powers"]
    market_shares       = sim_config["market_shares"]

    # Demand generator by normal distribution
    demand_distribution = sim_config["demand_distribution"]
    distribution_params = sim_config["distribution_params"][demand_distribution]
    
    params = {
        "t_max": t_max,
        "financed": financed,
        "paradigm": paradigm,
        "operation_fee": operation_fee,
        "loan_repayment_time": loan_repayment_time,
        "bank_annual_rate": bank_annual_rate,
        "invoice_annual_rate": invoice_annual_rate,
        "invoice_term": invoice_term,
        "window_size": window_size,
        "powers": powers,
        "market_shares": market_shares,
        "demand_distribution": demand_distribution,
        "distribution_params": distribution_params
    }
    return sim_id, topology, homogeneous, params



def grid_search_params(config_file):
    """
    Enumerate all valid combinations of parameters for grid search.
    """
    

# Network configuraitons
network_config = load_config_file("configs/network_config.yaml")

# # Single run
# sim_config = load_config_file("configs/simulation_config.yaml")
# (sim_id, topology, homogeneous, input_params) = single_run_params(sim_config)

# # New a simulation instance
# sim = SCFSimulation(sim_id=0,
#                     topology,
#                     homogeneous,
#                     network_config,
#                     **input_params)
# # Run the simulation
# sim.run()


# Grid search
input_params = load_config_file("configs/grid_search_inputs.yaml")
sim_configs = simconfig_generator(input_params)

for config in sim_configs:
    sim_id = config["sim_id"]
    topology = config["network_topology"]
    homogeneous = config["homogeneous"]

    config.pop("sim_id")
    config.pop("network_topology")
    config.pop("homogeneous")

    # Run simulation
    sim = SCFSimulation(sim_id,
                        topology,
                        homogeneous,
                        network_config,
                        **config)
    # Run the simulation
    sim.run()

    if sim_id == 2: break