# Supply Chain Financing Simulation

# Output Data Structure:
## File name
- output_`sim_unique_ID`.csv
- config_`sim_unique_ID`.yaml

## Input Parameters
- mean_demand 
- invoice_repayment_term 
- medium_company_sale_skew


## Output Columns
- `timestep`: int. The timestep this data is recorded at.
- `node_idx` = Node ID: int
- `cash` = Cash: float. Liquid cash of node at present time (t+0). I guess should be possible to define as max(recievables_(t+0)-payables_(t+0),0).
- `tier` = Tier: int. Shortest path from market node
- `power`: int. Power of node.
- `stock` = Inventory: int. Number of stores material units
- `unfilled` = Unfilled Orders: int. Stored number of orders that node still has to fill.
- `issued` = Issue orders: int. Stored number of orders that node has issued that have not been fulfilled.
- `buy_amount` = The actual amount in the new Orders: int. Number of new orders issued by that node at that given timestep.
- `receive_amount` = The actual amount receive: int. Number of new orders received by that node at that given timestep.
- `purchase_value` = New Purchase cost: float. The associated total price of a given purchase at a timestep
- `sale_value` = New Sale Value: float. The associated total price at a given timestep of all sales.
- `cash_from` = Sender of cash: int. The node which sends the money to another node.
- `pay_amount` = Amound of payment: float. The amount of payment from `cash_from` to the `node_idx`. 
- `is_bankrupt` = Bankrupt: bool. Denotes if a node has become bankrupt and hence removed from the simulation.
- `receivable` = Receivables: float. Recievables at timestep t0
- `payable` = Payables: float. Payables at timestep t0

a) Note, payables should be invoice payables + debt + operation fee
- `invoice_payables` = Invoice Payables: float. Invoice payables at time t0

a) note: invoice payable should be payables - debt
- `debt` = Debt: float. Debt payables, which is the principal debt plus interest. Sum of this produces the debt variable, used to check if the node is above the bank mandate.


## Analysis Pipeline:
A) Previous Paper Analysis

a) 
- First preprocess data st it is all numerical
- `Aggregate`: Find proportion of failures of each company type across all data
- `Piecewise`: Find mean of proportion of failures of each company type for each combination of parameters
- Return Pie Charts (other data representations recommendations acceptable)
- Determine KL divergence from theoretical distributions (Lattice: s:1/3, m:1/3, l:1/3 | Diamond: s:0.5, m:0.388888889, l:0.111111111 (approx.)) of `aggregate` and `piecewise` distributions

b)
- Survival time histograms on lattice for: small companies; medium companies; large companies; companies in networks that have no notion of company size (homogeneous)
- Survival time histograms on diamond for: ditto
- Superimpose curve of best fit (red) and next 5 best fitting curves (greyed out); mean
- return: parameters of best fit curves; mean; median; variance

- survival time histograms of system for diamond and lattice
- superimpose gaussian mixture model component curves and mixed curve; unimodal curve of best fit
- return: parameters of best fit curves; mean; median; variance; parameters of GMM

- Kernel density estimates of system survival times for lattice and diamond
topologies in days

c)
- moderated regression analysis of network object, topology, and paradigm vs product term, scf interest rate, bank interest rate, proactivity window

d)
- n boxplots per cell for given combos of inputs

B) Next paper analysis
a) Calculating the cash to cash cycle
- Current cash-to-cash cycle variable = sale_price_per_unit \*<stock_over_time_t> / ( sum(purchase_costs_over_time_t) + operational_fee\*t ) * t + <accounts_payable_over_time_t> / sum(sale_values_over_time_t) * t - sum(accounts_payable_over_time_t) / ( sum(purchase_costs_over_time_t) + operational_fee\*t ) * t
- <x> means mean of the set x
- I believe the first two terms can be simplified into sums (rather than means) not multiplied by the number of timesteps investigated but whatever
