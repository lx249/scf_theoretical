
# %% Load config parameters
import yaml
from simulation import SCFSimulation

def load_config_file(config_file_path, mode="r"):
    with open(config_file_path, mode) as file:
        config = yaml.safe_load(file)
    return config

sim_config = load_config_file("configs/simulation_config.yaml")
network_config_file = "configs/network_config.yaml"

sim_id = sim_config["simulation_ID"]
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
demand_generator = sim_config["demand_generator"]
params = distributions[demand_generator]

simulation = SCFSimulation(sim_id,  
                           network_config_file, 
                           t_max,
                           operation_fee, 
                           loan_repayment_time,
                           bank_annual_rate,
                           invoice_annual_rate,
                           invoice_term,
                           window_size,
                           powers,
                           demand_generator,
                           params)
simulation.run()
