"""
Runing simulation by using different combinations of input parameters.
Author: Liming Xu
Email: lx249@cam.ac.uk
"""

# %% 
import itertools 
from simulation import SCFSimulation
from utils import load_config_file


def is_valid(powers):
    """
    Check if the list `powers` is valid (undecreasing) or not.

    Parameters
    ----------
    `powers`: list
        The market share of small, medium, and large power.

    Returns
    -------
        bool: valid power combination or not.
    """
    return all( i<=j for i, j in zip(powers, powers[1: ]))


def get_valid_powers(small, medium, large):
    """
    Get all valid market share combinations 
    for small, medium and large power.
    """
    valid_powers = []
    all_powers = list(itertools.product(small, medium, large))
    for powers in all_powers:
        if is_valid(powers):
            valid_powers.append(powers)
    return valid_powers


def single_run_params(sim_config):
    """
    Return the parameters for a signle running.
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

# Get input params for a signle run of simulation
sim_config = load_config_file("configs/simulation_config.yaml")
(sim_id, topology, homogeneous, input_params) = single_run_params(sim_config)


# %% New simulation instance
%%timeit

sim = SCFSimulation(sim_id, 
                    topology, 
                    homogeneous, 
                    network_config, 
                    **input_params)
# Run the simulation 
sim.run()

# %%