# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 13:57:51 2021

@author: ZChen4

This script is for exploring different exogenous variables
This step needs assumptions on volitility model and error distribution
You can skip this step as you like
"""
###############################################################################
#%% Modules
###############################################################################
# System paths
import os, sys
sys.path.append(os.path.abspath('modules'))
# import scipy

# Global modules
import importlib                                        # Operating system
import pandas as pd                                     # Dataframes
import numpy as np                                      # Numeric Python
import arch                                             # ARCH/GARCH models

# ARCH package functional imports
from arch.univariate import (ARCH, GARCH, EGARCH, EWMAVariance, # Vol process
                              RiskMetrics2006) 
from arch.univariate import (Normal, StudentsT, # Distribution of residuals
                              SkewStudent, GeneralizedError)

# Ignore a certain type of warnings which occurs in ML estimation
from arch.utility.exceptions import (
    ConvergenceWarning, DataScaleWarning, StartingValueWarning,
    convergence_warning, data_scale_warning, starting_value_warning)

# Local modules
import distGARCH; importlib.reload(distGARCH)           # Distributional GARCH
from distGARCH import DistGARCH


# Pandas options
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 10)

# Warnings management
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

###############################################################################
#%% Local functions
###############################################################################
# Function to calculate log return
def logret(series): return(np.log(series/series.shift(1)))



###############################################################################
#%% Configuration
###############################################################################
# Start of series
start = '2010-07-09'

# End of series
end = None

# Assumed AR lag in mean model
lag_ar = [1]
# lag_ar = [1, 2, 3]

# Assumed volitylity model
vol_mod = ARCH(1)
#ARCH(1), EGARCH(1,1,1), GARCH(1), GARCH(1,1), EWMAVariance(None), RiskMetrics2006()

# Assumed distribution
dist_mod = StudentsT()
#Normal(), StudentsT(), SkewStudent(), GeneralizedError()


###############################################################################
#%% Data loading
###############################################################################
# Please put your data in data/clean folder
df = pd.read_csv('data/clean/gha.csv', parse_dates=['date'])

# Set date as index
df=df.set_index('date',drop=True).sort_index()

# Crop the data as needed
df = df.loc[start:end, ]

###############################################################################
#%% Configuration: Data Treatment
###############################################################################
# Dependent Variable
df['FX level'] = df['usdghs'].copy() #Please don't delete or change this line
# Dependent var in log return
# Please don't change the 10000 comes with the logret, because it makes it into bps
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

###############################################################################
#%% Configuration: Model specification
###############################################################################
# Please use the correct column names in the []!!!
microstructure = ['Bid ask abs', 'High low abs']

cip = microstructure + ['Interbank spread']

usdmove = cip + ['EURUSD log returns']

vix = usdmove + ['VIX fd']

baseline =  vix + ['Oil prices fd']

# List of exogenous variables model
models_l = [microstructure, cip, usdmove, vix, baseline]
# Give the above models more readable names. Please put the name in the correct order
labels_l =['Microstructure','Market volume','CIP', 'Dollar move', 'Risk Appetite', 'Baseline']

# Please don't change the following lines
all_var_l = list(set(sum(models_l, [])))

###############################################################################
#%% Model fitting and results saving
###############################################################################
specification_tables_short_l = list()


for label, model in zip(labels_l, models_l): # Loop for different exogenous specifications
    dgm = DistGARCH(depvar_str='FX log returns', # Name of dep var
                    data=df, # Dataframe to work on
                    level_str='FX level', # Name of level dep var
                    exog_l=model, # Exogenous model
                    lags_l=lag_ar, # Lag for AR term
                    vol_model= vol_mod, # Volitility model
                    dist_family=dist_mod) # Distribution innovation

    # Fit the model
    dgfit = dgm.fit()

    # Generate the tables
    var_d = dict()
    for i in lag_ar:
        var_d[f'FX l...rns[{i}]'] = f'Lag {i} FX log returns'
    lag_name_l = list(var_d.values())
    sumtable_short = dgfit.summary_table(model_name=label, var_d=var_d,
                                         print_pval=False)
    specification_tables_short_l.append(sumtable_short)

# Merge all the summary tables
dsum_short = pd.concat(specification_tables_short_l, axis=1)
dsum_short = dsum_short.reindex(lag_name_l+all_var_l+['R2','R2 adjusted', 'Intercept',
                                            'Alpa', 'Beta', 'Lambda','Nu','Omega', 'Eta',
                                           'lam', 'Number of observations'])

# Save the table
dsum_short.to_excel('output/step001_exogenous_variables_exploration_rtable.xlsx')


