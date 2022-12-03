import pandas as pd
import numpy as np

# The columns of the output dataframe. 
column_dtypes = [
    ("timestep", int),
    ("node_idx", int),
    ("tier", int),
    ("power", int),
    ("is_bankrupt", bool),
    ("stock", int),
    ("cash", float),
    ("order_from", int),
    ("buy_amount", int),
    ("purchase_value", float),
    ("sale_value", float),
    ("unfilled", int),  # Unfilled orders
    ("issued", int),  # Issued orders
    ("receivable", float),
    ("payable", float),
    ("debt", float)
]
columns = list(zip(*column_dtypes))[0]



class Writer(object):

    def __init__(self, sim_id, column_dtypes=column_dtypes):
        self.output_file = f"output_data/output__sim_{sim_id}.csv"
        self.output = pd.DataFrame(np.empty(0, dtype=np.dtype(column_dtypes)))


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
        self.output.to_csv(self.output_file, index=False)
        
    
        
