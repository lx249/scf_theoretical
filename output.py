import pandas as pd

# The columns of the output dataframe. 
columns = [
    "timestep", 
    "node_idx",
    "tier",
    "power",
    "is_bankrupt",
    "stock",
    "cash",
    "order_from",
    "buy_amount",
    "purchase_value", 
    "sale_value",
    "unfilled", # Unfilled orders
    "issued",  # Issued orders
    "receivable",
    "payable",
    "debt",
]


class Writer(object):

    def __init__(self, sim_id, columns=columns):
        self.output_file = f"output_data/output__sim_{sim_id}.csv"
        self.output = pd.DataFrame(columns=columns)

    def append(self, data_at_t):
        """
        Append data into the output dataframe.

        Parameters
        ---------
        `data_at_t`: dict
            the output data at a time step.
        """
        incoming_output = pd.DataFrame.from_dict(data_at_t)
        self.output = pd.concat([self.output, incoming_output], ignore_index=True)

    def write(self):
        self.output.to_csv(self.output_file)
        
    
        
