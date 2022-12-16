"""
Utility function for common use. 
Author: Liming Xu
Email: lx249@cam.ac.uk
"""
import yaml 

# %% Load config parameters
def load_config_file(config_file_path, mode="r"):
    with open(config_file_path, mode) as file:
        config = yaml.safe_load(file)
    return config
