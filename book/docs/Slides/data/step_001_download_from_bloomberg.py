# -*- coding: utf-8 -*-
"""
Download data from Bloomberg with Xbbg
You need to run this code from a machine with Bloomberg terminal installed
Should Install xbbg https://xbbg.readthedocs.io/en/latest/
Contact: romain.lafarguette@gmail.com
Time-stamp: "2023-04-07 18:47:50 A13258Q"
"""
###############################################################################
# %% Modules
###############################################################################
import os
import pandas as pd
import datetime

from xbbg import blp # https://xbbg.readthedocs.io/en/latest/

###############################################################################
# %% Download the data history of a list of tickers, up to today
###############################################################################
start_date = pd.to_datetime('1990-01-01') # Starting point
today = datetime.datetime.now().strftime('%Y-%m-%d') # Last point

# Dictionary of tickers with labels for easy manipulation
tickers_d = {
    
    # FX data
    'USDPHP REGN Curncy': 'usdphp_spot', # Use the regional pricing algo
    'EURUSD BGN Curncy': 'eurusd_spot', # BBG fixing (L160 only after 2007)
    'PPN+3M BGN Curncy': 'usdphp_fwd_outright_ndf', 

    # Interest rate data
    'PREF3MO Index': 'phn_3m_interbank_rate',
    'PH91AVG Index': 'phn_3m_tbill_yield',
    'PH5YAVE Index': 'phn_5y_tbond_yield',
    'P10YAVE Index': 'phn_10y_tbond_yield',

    'US0003M Index': 'usa_3m_libor_rate',
    'USGG3M Index': 'usa_3m_tbill_yield',
    'USGG5YR Index': 'usa_5y_tbond_yield',
    'USGG10Y Index': 'usa_10y_tbond_yield',
    
    # Vol data
    'USDPHPV1M BGN Curncy': 'usdphp_implied_vol_1m',
    'EURUSDV1M Curncy': 'eurusd_implied_vol_1m',
    'VIX Index': 'vix_index',

    # Misc
    'CL1 COMB Comdty': 'oil_future_price', # Bloomberg generic contracts
    
             }

frames_l = list()
for ticker, label in tickers_d.items():

    try:
        # Download historical data with bdh (history) from Bloomberg
        _db = blp.bdh(tickers=ticker,
                      flds=['PX_LAST', 'PX_BID', 'PX_ASK',
                            'PX_HIGH', 'PX_LOW'], 
                      start_date=start_date, end_date=today)
        
        _db.columns = [x[1] for x in _db.columns] # Flatten the columns

        # Add extra info with bdp (point)
        long_name = blp.bdp(tickers=ticker, flds=['Long_Comp_Name']).iloc[0, 0]

        _db.insert(0, 'label', label) # Easier for coding than the name
        _db.insert(1, 'bbg_ticker', ticker)
        _db.insert(2, 'long_name', long_name)
        frames_l.append(_db)
        
        print(f'{ticker} downloaded')
        
    except Exception as exc:
        print(f'Issue with {ticker}: {exc}')

# Concatenate the frame
df = pd.concat(frames_l, axis='index')

###############################################################################
# %% Export the raw data in csv
###############################################################################
d_p = os.path.abspath('c:/Users/A13258Q/OneDrive - ADIA/Teaching/varfxi/data/')
file_path = os.path.join(d_p, 'sti_fxi_raw_data.csv')
df.to_csv(file_path, encoding='utf-8', index=True)


