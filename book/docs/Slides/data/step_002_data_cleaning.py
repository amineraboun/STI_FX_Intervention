# -*- coding: utf-8 -*-
"""
Clean the Bloomberg data
Contact: romain.lafarguette@gmail.com
Time-stamp: "2023-04-08 11:55:56 A13258Q"
"""
###############################################################################
# %% Modules
###############################################################################
import os
import pandas as pd

pd.set_option('display.max_columns', 10)

###############################################################################
# %% Paths
###############################################################################
d_p = os.path.abspath('c:/Users/A13258Q/OneDrive - ADIA/Teaching/varfxi/data/')
file_path = os.path.join(d_p, 'sti_fxi_raw_data.csv')

###############################################################################
# %% Load the raw data, long format
###############################################################################
dlong = pd.read_csv(file_path, parse_dates=[0], index_col=[0])

###############################################################################
# %% Reshape the data in wide format
###############################################################################
# Main frame: Data frame of last prices (PX LAST) only
df = dlong.pivot_table(index=dlong.index,
                       columns=['label'], values='PX_LAST')

# Compute the bid-ask spread
dbid = dlong.pivot_table(index=dlong.index,
                         columns=['label'], values='PX_BID')

dask = dlong.pivot_table(index=dlong.index,
                         columns=['label'], values='PX_ASK')

# Create a new frame with the bid-ask spread
dba = pd.DataFrame(index=dbid.index)
for _var in dbid.columns:
    dba[_var] = dbid[_var] - dask[_var]
    
# Rename the bid-ask variables
dba.columns = [f'{x}_bid_ask' for x in dba.columns]

#  Merge some bid-ask variables with the main frame
ba_l = ['usdphp_spot_bid_ask', 'eurusd_spot_bid_ask']
df = df.merge(dba[ba_l], how='left', left_index=True, right_index=True)

###############################################################################
# %% Compute a few key metrics
###############################################################################
# Ted spread: 10y - 3m
df['php_ted_spread'] = df['phn_5y_tbond_yield'] - df['phn_3m_tbill_yield']
df['usa_ted_spread'] = df['usa_10y_tbond_yield'] - df['usa_3m_tbill_yield']

# Interest rate differenial
df['php_usa_short_rate_diff'] = (df['phn_3m_interbank_rate']
                                 - df['usa_3m_libor_rate'])

# Forward carry
fwd = df['usdphp_fwd_outright_ndf']
spot = df['usdphp_spot']
df['php_fwd_carry'] = (fwd - spot)/spot

###############################################################################
# %% Export the data
###############################################################################
d_p = os.path.abspath('c:/Users/A13258Q/OneDrive - ADIA/Teaching/varfxi/data/')
clean_path = os.path.join(d_p, 'sti_fxi_clean_data.csv')
df.to_csv(clean_path, encoding='utf-8', index=True)












