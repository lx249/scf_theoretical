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


  
## Future plan
### 
- n-hop region
- nodes share financing threshold to focal node of subregion
- node optimises

a) Calculating the cash to cash cycle
- Current cash-to-cash cycle variable = `sale_price_per_unit` \* `stock_over_time_t` / `(sum(purchase_costs_over_time_t)` + `operational_fee`\*`t` ) * `t` + <`accounts_payable_over_time_t`> / `sum(sale_values_over_time_t)` * `t` - `sum(accounts_payable_over_time_t)` / `(sum(purchase_costs_over_time_t) + `operational_fee \* t )` * `t`
- <x> means mean of the set x
- I believe the first two terms can be simplified into sums (rather than means) not multiplied by the number of timesteps investigated but whatever
    
a') May be worth investigating comparison of cash-to-cash-cycle minimisation survivability vs recievables to payables time series difference minimisation survivability
    
b) Local visibility
  - n-hop region
  - nodes share financing threshold to subregion focal node
  - focal nodes then use information to redefine their own financing threshold
  
c) 2 step cash2cash optimisation cycle for focal node n
  - notation
  - - let $ft(t, n)$ = financing threshold that time t of node n
  - - D = gradient function
  - - $n_i$ = node $i$
  - - $L$ = local region
  - $c2c(t,n) = f({ft(n,t)_[n in L]})$
 
c1) Optimise ft(t,n)
  - $c2c(t',n) = f( {ft(n_i,t)_[n in {L\n}], argmin_[ft](ft(n,t)Dft(n,t'))} )$
  - basically, adjust $ft(n,t)$ in a way that maximally reduces c2c assuming c2c can be defined in terms of $f$
  
c2) Optimise D
  - $c2c(t+1,n) = argmin_[f](f( {ft(n_i,t)_[n in {L\n}], ft(n,t')} )$
  - basically, adjust $f$ in a way that maximally reduces c2c assuming it can be defined in terms of $f$
  
c3) Options for f
  - linear combination of financing thresholds of each member with weights
  - - eg, $f({ft(n,t)_[n in L]}) = sum_[i in L]( g_i^(t) ft(n,t) )$
  - vitality function that measures difference between some weighted graph connectivity measure and same measure on graph without focal node (probably comparing impact of vitality versus not is its own study)
  - softmax, or something, whatever that function might be
  
d1) Proposed steady state parameterisation (for material functions, not financial ones, I don't know if those even have meaningful steady state parameters)
  - If operative costs per timestep equal expected profits per timestep, then in this parameter configuration we, up to approximation, can say with confidence that all failures are due to variation and not magnitude of market behaviour
  - `o = operating_fee`; `m = mean_demand`; `N = nodes_in_network`; $M_n$ = nodes_in_path_upstream_of_n_inclusive; $r_m$ = relative_market_share_of_node_m
  - Option $a: o = m * sum_[n in N](product_[m in M_n](r_m)) / |N|$
  - - that is if we wish to give everyone the same operating fee
  - denoting $o_n$ = operative_fee_of_n
  - Option b: $o_n$ = $m * product_[m in M_n](r_m)$
  - - that is if we wish to give everyone unique operative fees (no mean field assumption)
  - Option c: Whatever Liming suggests for empirically derived steady state parameterisation manifold
  
d2) Operative fee scale parameter
  - I propose that we introduce a scale parameter, s,  for operative fee if we use this equilibrium state to be able to conduct easy sensitivity analysis
  - Default $s = 1$, st $real_operative_fee = s*o or s*o_n$
