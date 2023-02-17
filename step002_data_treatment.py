# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 14:02:27 2022

@author: ZChen4

This script is for data treatment
Please change the data treatment accordingly and pay attention to indentation
You dont need to run this script
"""
###############################################################################
#%% Modules
###############################################################################
import numpy as np                                      # Numeric Python

###############################################################################
#%% Local functions
###############################################################################

# Function to calculate log return
def logret(series): return(np.log(series/series.shift(1)))


###############################################################################
#%% Configuration: Data Treatment 
###############################################################################
def data_treatment(df):
    # Dependent Variable
    # The level data is needed. Please don't delete
    df['FX level'] = df['usdghs'].copy()
    # Dependent var in log return
    # Please don't change the 10000, beacuse it turns it into bps
    df['FX log returns'] = 10000*logret(df['usdghs'])

    # Bid ask spread calculation
    df['Bid ask abs'] = np.abs(df['usdghs_bid']-df['usdghs_ask'])
    
    # High low spread calculation
    df['High low abs'] = np.abs(df['usdghs_high']-df['usdghs_low'])
    
    # Dollar movement
    df['EURUSD log returns'] = 10000*logret(df['eurusd'])
    
    # CIP
    df['Interbank spread'] = df['gha_interbank'] - df['effr']

    # First differnce on vix
    df['VIX fd'] = df['vix'].diff(1)
    
    # First diff of oil price
    df['Oil prices fd'] = df['oil_p'].diff(1)
    

 
