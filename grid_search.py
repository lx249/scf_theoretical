
# %% Load config parameters
import yaml
import itertools 
from simulation import SCFSimulation

def load_config_file(config_file_path, mode="r"):
    with open(config_file_path, mode) as file:
        config = yaml.safe_load(file)
    return config


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



# Input parameters
sim_config = load_config_file("configs/simulation_config.yaml")
network_config_file = "configs/network_config.yaml"

sim_id              = sim_config["sim_id"]
network_topology    = sim_config["network_topology"]
node_homogenity     = sim_config["node_homogenity"]
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
distributions = sim_config["distributions"]
demand_generator = sim_config["demand_generator"]
params = distributions[demand_generator]


# New simulation instance
%time
simulation = SCFSimulation(sim_id,  
                           network_config_file, 
                           network_topology,
                           node_homogenity,
                           t_max,
                           financed,
                           paradigm,
                           operation_fee, 
                           loan_repayment_time,
                           bank_annual_rate,
                           invoice_annual_rate,
                           invoice_term,
                           window_size,
                           powers,
                           market_shares,
                           demand_generator,
                           params)
# Run the simulation.
simulation.run()
