# -*- coding: utf-8 -*-
"""
Created on Sun Jul 31 20:34:53 2022

@author: ZChen4

This scrpit will perform model combination and generate related charts
"""

###############################################################################
#%% Modules
###############################################################################
# System paths
import os, sys
sys.path.append(os.path.abspath('modules'))

# Global modules
import importlib                                        # Operating system
import pandas as pd                                     # Dataframes
import numpy as np                                      # Numeric Python
import datetime                                         # Dates
import arch                                             # ARCH/GARCH models
from scipy import interpolate
import shelve
from scipy.stats import iqr

# Ignore a certain type of warnings which occurs in ML estimation
from arch.utility.exceptions import (
    ConvergenceWarning, DataScaleWarning, StartingValueWarning,
    convergence_warning, data_scale_warning, starting_value_warning)

# Local modules
import distGARCH; importlib.reload(distGARCH)           # Distributional GARCH
from distGARCH import DistGARCH


import lib
import imfplotly
importlib.reload(lib)
# Graphics
import matplotlib.pyplot as plt                         # Graphical package  
import seaborn as sns                                   # Graphical tools

# Graphics options
plt.rcParams["figure.figsize"] = 25,15

# Pandas options
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 10)

# Warnings management
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

# Import data treatment
import step002_data_treatment as dat_tm

###############################################################################
#%% Load in important results from step003
###############################################################################
my_shelf = shelve.open('intermediary results/step003_crucial_results.out')
for key in my_shelf:
    globals()[key]=my_shelf[key]
my_shelf.close()

###############################################################################
#%% Configuration
###############################################################################
# Start of series
start = '2000-01-01'
# start = '2013-01-21'

# End of series
end = None

# Please provide a date you want to based the 1-day ahead forcast on
# For example, you want to get the VaR at '2022-07-15'
# So the forecast_based_on_date should be '2022-07-14'
forecast_based_on_date = '2023-01-06'
    
# Upper threshold for distribution
ut = 0.975

# Lower threshold for distribution
lt = 0.025

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
#%% Data treatment
###############################################################################
dat_tm.data_treatment(df)

###############################################################################
#%% Checking whether the date are availabel in all models
###############################################################################
exo_dict = dict(zip(exo_labels_l,exo_spec_l))
vol_dict = dict(zip(vol_labels_l, vol_spec_l))
errdist_dict = dict(zip(errdist_labels_l, errdist_l))

for spec in  selected_both_spec_l:
    exo_model= exo_dict[spec[0]]
    df_check = df[exo_model].dropna()
    try:
        df_check.loc[forecast_based_on_date]
    except:
        print('The date you provided has not enough info to do forecast. Please input a new date')
        break
    
###############################################################################
#%% Run combined list and forecast on the above forecast_based_on_date
###############################################################################
# Traget date is just 1 day ahead of the forecast_based_on_date
target_date_date = datetime.datetime.strptime(forecast_based_on_date, '%Y-%m-%d')+ datetime.timedelta(days = 1)
target_date = target_date_date.strftime('%Y-%m-%d')

forecasted_dict = dict()
for spec in  selected_both_spec_l: # Loop over the combined pool
    exo_model= exo_dict[spec[0]]
    vol_model= vol_dict[spec[1]]
    dist= errdist_dict[spec[2]]
    model_name=spec[0]+' ['+spec[1]+', '+spec[2]+']'
    dg = DistGARCH(depvar_str='FX log returns', # Name of dep var
                                data=df, # Dataframe to work on
                                level_str='FX level', # Name of level dep var
                                exog_l=exo_model, 
                                lags_l=lag_ar , # Lag for AR term
                                vol_model= vol_model,
                                dist_family=dist)
    
    # Use all dates to tarin the model
    dgf = dg.fit()
    dgfor = dgf.forecast(forecast_based_on_date, horizon=1)
    dgfor_df = dgfor.dfor
    dgfor_df = dgfor_df.loc[[forecast_based_on_date]]
    forecasted_dict[model_name] = dgfor_df

# Forecast table for two slected model lists  
forecasted_df = pd.concat(forecasted_dict)
forecasted_df = forecasted_df.droplevel(1)

###############################################################################
#%% Calculated the weighted average of conditional mean
###############################################################################
# Subset out the selected mean model and mean value column
forecasted_mean_w_df = pd.merge(mean_selected_table, forecasted_df['cond_mean'], left_index=True, right_index=True, how='left')

## Drop predicted values that are obvious outliers
# Threshold for outliers
low_t = np.quantile(forecasted_mean_w_df['cond_mean'],0.25) - 1.5*iqr(forecasted_mean_w_df['cond_mean'])
high_t = np.quantile(forecasted_mean_w_df['cond_mean'],0.75) + 1.5*iqr(forecasted_mean_w_df['cond_mean'])

# Filter out outliers
forecasted_mean_w_df.loc[(forecasted_mean_w_df['cond_mean']>high_t)|(forecasted_mean_w_df['cond_mean']<low_t),'outlier'] = True
forecasted_mean_w_df['outlier'] = forecasted_mean_w_df['outlier'].fillna(False)
forecasted_mean_w_df = forecasted_mean_w_df.loc[forecasted_mean_w_df['outlier']==False,:]

# Re-calculate the weight for the combination pool
mean_selected_sum = (1/forecasted_mean_w_df['Cross Validation Out-sample RMSE (COND MEAN)']).sum()
forecasted_mean_w_df['Weight'] = (1/forecasted_mean_w_df['Cross Validation Out-sample RMSE (COND MEAN)'])/mean_selected_sum
mean_selected_table = forecasted_mean_w_df[['Cross Validation Out-sample RMSE (COND MEAN)', 'Threshold', 'Included',
       'Weight']]
mean_selected_table.to_csv('output/step003_combination_pool_for_mean.csv')

# Weighted average of conditional mean
forecasted_mean_w_df['weight_mean'] = forecasted_mean_w_df['Weight']*forecasted_mean_w_df['cond_mean']
forecasted_mean_val = np.nansum(forecasted_mean_w_df['weight_mean'])

forecasted_mean_w_df.to_csv('intermediary results/step004a_forecasted_mean_w_df.csv')

# Generate selected models vs NAIVE chart
sns.set(style='white', font_scale=2, palette='deep', font='serif') 
fig, ax = plt.subplots()

forecasted_mean_naive_df = mean_selected_table[['Cross Validation Out-sample RMSE (COND MEAN)']].copy()
if new_naive_config not in forecasted_mean_w_df.index.tolist():
    forecasted_mean_naive_df.loc[new_naive_config, 'Cross Validation Out-sample RMSE (COND MEAN)'] = naive_rmse

forecasted_mean_naive_df['Distance'] = naive_rmse/forecasted_mean_naive_df
forecasted_mean_naive_df = forecasted_mean_naive_df.sort_values('Distance')
plt.axvline(x=1.0, ls='--', color='grey', alpha=0.7)
for i in range(0, len(forecasted_mean_naive_df)):
    if(forecasted_mean_naive_df.iloc[i,1] > 1.0):
        plt.scatter(forecasted_mean_naive_df.iloc[i,1], forecasted_mean_naive_df.index[i],  marker='o', color='green')
    elif(forecasted_mean_naive_df.iloc[i,1] == 1.0):
        plt.scatter(forecasted_mean_naive_df.iloc[i,1], forecasted_mean_naive_df.index[i],  marker='v', color='red')
    else:
        plt.scatter(forecasted_mean_naive_df.iloc[i,1], forecasted_mean_naive_df.index[i],  marker='o', color='blue')
plt.ticklabel_format(style='plain', useOffset=False, axis='x')  
plt.savefig('output/step004a_naive_compared_rmse', bbox_inches='tight')
plt.savefig('output/step004a_naive_compared_rmse.pdf', bbox_inches='tight')
plt.show()
###############################################################################
#%% Calculated the weighted average of quantiles of conditional density
###############################################################################
# Subset out the selected mean model and quantile columns
col_l = ['cond_mean', 'cond_var']+[x for x in forecasted_df.columns.tolist() if ('cond_quant' in x)]
forecasted_density_w_df = pd.merge(density_selected_table, forecasted_df[col_l], left_index=True, right_index=True, how='left')

# Weighted average of quantiles of conditional density
forecasted_density_w_df_final = forecasted_density_w_df[col_l].multiply(forecasted_density_w_df['Weight'], axis=0)
forecasted_density_val_df = forecasted_density_w_df_final.sum(axis=0)

forecasted_density_w_df.index.name = 'Index'
forecasted_density_w_df_final.index.name = 'Index'

forecasted_density_w_df.to_csv('intermediary results/step004a_forecasted_density_w_df.csv')
forecasted_density_w_df_final.to_csv('intermediary results/step004a_forecasted_density_w_df_final.csv')

# Generate selected models vs NAIVE chart
sns.set(style='white', font_scale=2, palette='deep', font='serif') 
fig, ax = plt.subplots()

forecasted_density_naive_df = density_selected_table[['Cross Validation Out-sample MIS']].copy()
if new_naive_config not in forecasted_density_w_df_final.index.tolist():
    forecasted_density_naive_df.loc[new_naive_config, 'Cross Validation Out-sample MIS'] = naive_mis

forecasted_density_naive_df['Distance'] = naive_mis/forecasted_density_naive_df
forecasted_density_naive_df = forecasted_density_naive_df.sort_values('Distance')
plt.axvline(x=1.0, ls='--', color='grey', alpha=0.7)
for i in range(0, len(forecasted_density_naive_df)):
    if(forecasted_density_naive_df.iloc[i,1] > 1.0):
        plt.scatter(forecasted_density_naive_df.iloc[i,1], forecasted_density_naive_df.index[i],  marker='o', color='green')
    elif(forecasted_density_naive_df.iloc[i,1] == 1.0):
        plt.scatter(forecasted_density_naive_df.iloc[i,1], forecasted_density_naive_df.index[i],  marker='v', color='red')
    else:
        plt.scatter(forecasted_density_naive_df.iloc[i,1], forecasted_density_naive_df.index[i],  marker='o', color='blue')
plt.ticklabel_format(style='plain', useOffset=False, axis='x')

plt.savefig('output/step004a_naive_compared_mis', bbox_inches='tight')
plt.savefig('output/step004a_naive_compared_mis.pdf', bbox_inches='tight')
plt.show()

###############################################################################
#%% Synthesize Plot
###############################################################################

# Get CDF plot from the combined quaniles
con_col_l =  [x for x in forecasted_density_val_df.index.tolist() if ('cond_quant' in x)]
forecasted_quant_df = forecasted_density_val_df[con_col_l].copy().reset_index()
forecasted_quant_df['index']=[float(x.split('_')[2]) for x in forecasted_quant_df['index']]
forecasted_quant_df.columns=['prob','xval']

# Get the Density Plot
x = forecasted_quant_df['xval']
y = forecasted_quant_df['prob']

# Ddifferentiating the cdf to get pdf
dydx = np.diff(y)/np.diff(x)

pdf_df = pd.DataFrame(columns=['x_support','y_val'])

pdf_df['x_support'] = x.tail(-1)
pdf_df['y_val'] = dydx

pdf_df = pdf_df.apply(pd.to_numeric)

    
# Smooth the Density Plot and add annotation
sns.set(style='white', font_scale=2, palette='deep', font='serif') 
fig, ax = plt.subplots()
x_new = np.linspace(pdf_df['x_support'].min(), pdf_df['x_support'].max(), 1000)
bspline = interpolate.make_interp_spline(pdf_df['x_support'], pdf_df['y_val'])
y_new = bspline(x_new)

df = pd.DataFrame(index=x_new)
col = 'Combined_density'
df[col] = y_new

plt.plot(x_new, y_new, label='Combined density')
ax.axvline(forecasted_mean_val, ls='--', color='tab:green', label=f'Combined mean: {round(forecasted_mean_val,2)}')

lower_bound = forecasted_quant_df.loc[forecasted_quant_df['prob']==lt,'xval'].values[0]
plt.vlines(lower_bound, 0, bspline(lower_bound), ls='--', color='tab:red')
plt.fill_between(x_new, 0, bspline(x_new), where=(x_new<=lower_bound), color='tab:red', label=f'{lt*100} pct')
ax.text(0.99*lower_bound, 0, '{:.1f}'.format(lower_bound),
                horizontalalignment='left', color='darkred',
                verticalalignment='top')

upper_bound = forecasted_quant_df.loc[forecasted_quant_df['prob']==ut,'xval'].values[0]
plt.vlines(upper_bound, 0, bspline(upper_bound), ls='--', color='tab:red')
plt.fill_between(x_new, 0, bspline(x_new), where=(x_new>=upper_bound), color='tab:red', label=f'{ut*100} pct')
ax.text(0.99*upper_bound, 0, '{:.1f}'.format(upper_bound),
                horizontalalignment='left', color='darkred',
                verticalalignment='top')

plt.legend()
plt.title(f'Forecast for {target_date} based on information of {forecast_based_on_date}')

# Save the plot
plt.savefig('output/step004a_combined_density_w_combined_mean', bbox_inches='tight')

plt.savefig('output/step004a_combined_density_w_combined_mean.pdf', bbox_inches='tight')

plt.show()


# For HTML: objects.append(fig)
title = (f'Forecast for {target_date} based on information of {forecast_based_on_date}')

fig_combined_density1 = lib.plot_combined_density(df,forecasted_mean_val,lower_bound,upper_bound, title=title)

###############################################################################
#%% Synthesize plot shifted by combined mean 
###############################################################################
# Get CDF plot from the combied quaniles
con_col_l =  [x for x in forecasted_density_val_df.index.tolist() if ('cond_quant' in x)]

forecasted_quant_df = forecasted_density_val_df[con_col_l].copy().reset_index()

forecasted_quant_df['index']=[float(x.split('_')[2]) for x in forecasted_quant_df['index']]

forecasted_quant_df.columns=['prob','xval']


sift_dis = forecasted_mean_val - forecasted_quant_df.loc[forecasted_quant_df['prob']==0.5,'xval'].values[0]

forecasted_quant_df['xval'] = forecasted_quant_df['xval'] + sift_dis

# Get the Density Plot
x = forecasted_quant_df['xval']
y = forecasted_quant_df['prob']

dydx = np.diff(y)/np.diff(x)

pdf_df = pd.DataFrame(columns=['x_support','y_val'])

pdf_df['x_support'] = x.tail(-1) 
pdf_df['y_val'] = dydx

pdf_df = pdf_df.apply(pd.to_numeric)

# Smooth the Density Plot and add annotation
sns.set(style='white', font_scale=2, palette='deep', font='serif') 

fig, ax = plt.subplots()
x_new = np.linspace(pdf_df['x_support'].min(), pdf_df['x_support'].max(), 1000)
bspline = interpolate.make_interp_spline(pdf_df['x_support'], pdf_df['y_val'])
y_new = bspline(x_new)
df = pd.DataFrame(index=x_new)
col = 'Combined_density'
df[col] = y_new

plt.plot(x_new, y_new, label='Combined density')
plt.vlines(forecasted_mean_val, 0, bspline(forecasted_mean_val), ls='--', color='tab:green', label=f'Combined mean: {round(forecasted_mean_val,2)}')
lower_bound = forecasted_quant_df.loc[forecasted_quant_df['prob']==lt,'xval'].values[0]
plt.vlines(lower_bound, 0, bspline(lower_bound), ls='--', color='tab:red')
plt.fill_between(x_new, 0, bspline(x_new), where=(x_new<=lower_bound), color='tab:red', label=f'{lt*100} pct')
ax.text(0.99*lower_bound, 0, '{:.1f}'.format(lower_bound),
                horizontalalignment='left', color='darkred',
                verticalalignment='top')

upper_bound = forecasted_quant_df.loc[forecasted_quant_df['prob']==ut,'xval'].values[0]
plt.vlines(upper_bound, 0, bspline(upper_bound), ls='--', color='tab:red')
plt.fill_between(x_new, 0, bspline(x_new), where=(x_new>=upper_bound), color='tab:red', label=f'{ut*100} pct')
ax.text(0.99*upper_bound, 0, '{:.1f}'.format(upper_bound),
                horizontalalignment='left', color='darkred',
                verticalalignment='top')

plt.legend()
plt.title(f'Forecast for {target_date} based on information of {forecast_based_on_date}')

#Save the plot
plt.savefig('output/step004a_combined_density_shifted_by_combined_mean', bbox_inches='tight')
plt.savefig('output/step004a_combined_density_shifted_by_combined_mean.pdf', bbox_inches='tight')
plt.show()

title = (f'Forecast for {target_date} based on information of {forecast_based_on_date}')

fig_combined_density2 = lib.plot_combined_density(df,forecasted_mean_val,lower_bound,upper_bound, title=title)
###############################################################################
#%% Save important variables
###############################################################################
import shelve

filename='intermediary results/step004a_crucial_results.out'
my_shelf = shelve.open(filename,'n') 

for key in ['fig_combined_density1','fig_combined_density2','forecasted_mean_w_df','target_date','forecast_based_on_date',
            'mean_selected_table', 'forecasted_density_naive_df', 'forecasted_mean_naive_df']:
    try:
        my_shelf[key] = globals()[key]
    except TypeError:
        #
        # __builtins__, my_shelf, and imported modules can not be shelved.
        #
        print('ERROR shelving: {0}'.format(key))

