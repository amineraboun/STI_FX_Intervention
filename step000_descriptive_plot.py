# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 11:00:40 2022

@author: ZChen4

This scrpit is to generate a three-panel descriptive chart which contains information
of: (1) historical level, (2) historical log return and (3) historical KDE distribution
"""

###############################################################################
#%% Modules
###############################################################################
import pandas as pd                                     # Dataframes
import numpy as np                                      # Numeric Python

# Graphics
import matplotlib.pyplot as plt                         # Graphical package  
import seaborn as sns                                   # Graphical tools

# Graphics options
plt.rcParams["figure.figsize"] = 25,15
sns.set(style='white', font_scale=2, palette='deep', font='serif') 

# Pandas options
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 10)

import scipy.stats as st

###############################################################################
#%% Local functions
###############################################################################
# Function to calculate log return
def logret(series): return(np.log(series/series.shift(1)))



###############################################################################
#%% Configuration
###############################################################################
# Start of series
start = '2000-01-01'
# start =None

# End of series
end = None


# Upper threshold for distribution
ut = 0.975

# Lower threshold for distribution
lt = 0.025

# Specify the name of currency pair (will appear on the chart)
currency_pair = 'USDGHS'

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
#%% Data Treatment
###############################################################################
# Crop series if necessary
df_des = df.loc[start:end,:].copy().sort_index()

# Dependent Variable
# The level data is needed for descriptive plot
df_des['FX level'] = df_des['usdghs'].copy()

# Dependent var in log return
df_des['FX log returns'] = 10000*logret(df_des['usdghs'])

# For HTML report
df_des.to_csv('output/step000_df_des.csv')

###############################################################################
#%% Descriptive plot style control and initialization
###############################################################################
sns.set(style='white', font_scale=2, palette='deep', font='serif') 

fig, (ax1, ax2, ax3) = plt.subplots(3,1)

plt.subplots_adjust(hspace=0.60)

###############################################################################
#%% Panel 1 and 2: Level and Return
###############################################################################
ax1.plot(df_des.index, df_des['FX level'])
ax1.set_title('Historical FX Level', y=1.02)
ax1.set_ylabel(f'{currency_pair}')


ax2.plot(df_des.index, df_des['FX log returns'])
ax2.set_title('Historical FX Returns', y=1.02)
ax2.set_ylabel('Bps')

###############################################################################
#%% Panel 3 KDE Distribution
###############################################################################
kde_df_raw = df_des['FX log returns'].dropna()

# Generate KDE X Y Value
kde = st.gaussian_kde(kde_df_raw)
x_support = np.linspace(kde_df_raw.min(),kde_df_raw.max(),1000)
kde_df = pd.DataFrame({'X':x_support, 'Y':kde.pdf(x_support)})

# Get mode 
kde_mode_val = kde_df.loc[kde_df['Y']==kde_df['Y'].max(),'X'].values[0]

# Get 'CDF' X Y Value
cdf_kde = np.vectorize(lambda x: kde.integrate_box_1d(-np.inf, x))
kde_cdf_df = pd.DataFrame({'X':x_support, 'CDF':cdf_kde(x_support)})

# Get threshold X value
if sum(kde_cdf_df['CDF']==lt)==1:
    kde_low_b_xval = kde_cdf_df.loc[kde_cdf_df['CDF']==lt,'X'].values[0]
elif sum((kde_cdf_df['CDF']>=(lt-0.001))&(kde_cdf_df['CDF']<=(lt+0.001)))==1:
    kde_low_b_xval = kde_cdf_df.loc[(kde_cdf_df['CDF']>=(lt-0.001))&(kde_cdf_df['CDF']<=(lt+0.001)),'X'].values[0]
else:
    kde_low_b_xval = np.mean(kde_cdf_df.loc[(kde_cdf_df['CDF']>=(lt-0.001))&(kde_cdf_df['CDF']<=(lt+0.001)),'X'])

# Get threshold X value
if sum(kde_cdf_df['CDF']==ut)==1:
    kde_up_b_xval = kde_cdf_df.loc[kde_cdf_df['CDF']==ut,'X'].values[0]
elif sum((kde_cdf_df['CDF']>=(ut-0.001))&(kde_cdf_df['CDF']<=(ut+0.001)))==1:
    kde_up_b_xval = kde_cdf_df.loc[(kde_cdf_df['CDF']>=(ut-0.001))&(kde_cdf_df['CDF']<=(ut+0.001)),'X'].values[0]
else:
    kde_up_b_xval = np.mean(kde_cdf_df.loc[(kde_cdf_df['CDF']>=(ut-0.001))&(kde_cdf_df['CDF']<=(ut+0.001)),'X'])

# Plotting
ax3.plot(x_support, kde.pdf(x_support), label=f'Mode: {round(kde_mode_val,2)}\n2.5 pct: {round(kde_low_b_xval,2)}\n97.5 pct: {round(kde_up_b_xval,2)}')
ax3.hist(kde_df_raw, density =True, bins=100)
ax3.legend()
ax3.set_title('Kernel Density Estimation of the Historical FX Returns', y=1.02)
ax3.set_ylabel('Density')


###############################################################################
#%% Save plot
###############################################################################
plt.savefig('output/step000_hostorical_descriptive_plot', bbox_inches='tight')


###############################################################################
#%% Save important variables
###############################################################################
import shelve

filename='intermediary results/step000_crucial_results.out'
my_shelf = shelve.open(filename,'n') 

for key in ['currency_pair']:
    try:
        my_shelf[key] = globals()[key]
    except TypeError:
        #
        # __builtins__, my_shelf, and imported modules can not be shelved.
        #
        print('ERROR shelving: {0}'.format(key))
