# -*- coding: utf-8 -*-
"""
Created on Sun Jul 31 20:34:53 2022

@author: ZChen4

This scrpit will generate related charts using the best density model
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
import datetime                                         # Dates
import arch                                             # ARCH/GARCH models
import lib
importlib.reload(lib)
import imfplotly
import shelve


# Ignore a certain type of warnings which occurs in ML estimation
from arch.utility.exceptions import (
    ConvergenceWarning, DataScaleWarning, StartingValueWarning,
    convergence_warning, data_scale_warning, starting_value_warning)

# Local modules
import distGARCH; importlib.reload(distGARCH)           # Distributional GARCH
from distGARCH import DistGARCH


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
forecast_based_on_dateb = forecast_based_on_date

# There will be some plots showing some dynamics over time
# Please provide a start date for these dynamic
# For best performance, please provide a date which is at least 30 days ahead the end
dynamic_start = '2022-10-01'


# Upper threshold for distribution
ut = 0.975

# Lower threshold for distribution
lt = 0.025


## For certain dynamics over time plots, you can set the dynamics as in sample or out of sample
## If you want an in-sample plot, please set e.g. jp_out_sample = False
## If you want an out-sample plot, please set e.g. jp_out_sample = True

# Out sample joyplot?
jp_out_sample = True

# Out sample fanchart?
fc_out_sample = True

# Out sample CDF plot?
cd_out_sample = True

# Out sample conditional VaR exceedance plot?
cdv_out_sample = True

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
#%% Get BEST DENSITY MODEL 
###############################################################################
# Get specification name
best_density_spec_string = density_selected_table.index.tolist()[0]
split_string = best_density_spec_string.split(' [')
vol_dist_l = split_string[1].rstrip(']').split(', ')
exo_mod = split_string[0]
vol_mod = vol_dist_l[0]
dist_mod = vol_dist_l[1]

###############################################################################
#%% Checking wether the forecast_based_on_date is availabel in the best model. 
###############################################################################
exo_col_l= exo_dict[exo_mod]
df_check = df[exo_col_l].dropna()
try:
    df_check.loc[forecast_based_on_date]
except:
    print('The forecast_based_on_date you provided has not enough info to do forecast. Please input a new date')

       
###############################################################################
#%% Fit the model
###############################################################################
exo_model = exo_dict[exo_mod]
vol_model = vol_dict[vol_mod]
dist_model = errdist_dict[dist_mod]


#### Specify the model
dg = DistGARCH(depvar_str='FX log returns',
                data=df,
                level_str='FX level', 
                exog_l=exo_model, 
                lags_l=lag_ar, 
                vol_model=vol_model,
                dist_family=dist_model)

dgf = dg.fit()
# Fit the model

# Please a date with all independent var present
dgfor = dgf.forecast(forecast_based_on_date, horizon=1)
 

##########################################################
#%% Plotting
###############################################################################
###############################################################################
#%% The PIT Plot
###############################################################################
# Style
sns.set(style='white', font_scale=2, palette='deep', font='serif') 
# Plot
dgfor.pit_plot(title= '')

# Save the figure
pitchart_f = os.path.join('output', 'step004b_pitchart.pdf')
plt.savefig(pitchart_f, bbox_inches='tight')
pitchart_f = os.path.join('output', 'step004b_pitchart.png')
plt.savefig(pitchart_f)
plt.show()

# Create HTML version
fig_pit = lib.create_pit_plot(dgfor)



###############################################################################
#%% Value at Risk Plot for a specific date of the above baseline model
###############################################################################

# Traget date is just 1 day ahead of the forecast_based_on_date
target_date_date = datetime.datetime.strptime(forecast_based_on_date, '%Y-%m-%d')+ datetime.timedelta(days = 1)
target_date = target_date_date.strftime('%Y-%m-%d')
target_dateb = target_date
sns.set(style='white', font_scale=2, palette='deep', font='serif') 
dgfor.plot_pdf_rule(fdate=forecast_based_on_date, q_low=lt, q_high=ut)

# Save the figure
var_rule_f = os.path.join('output', 'step004b_var_rule.pdf')
plt.title(f'Forecast for {target_date} based on information of {forecast_based_on_date}')
plt.savefig(var_rule_f, bbox_inches='tight')


var_rule_f = os.path.join('output', 'step004b_var_rule.png')
plt.savefig(var_rule_f)
plt.show()

# Create HTML version of PDF
ttle = f'Forecast for {target_date} based on information of {forecast_based_on_date}'

fig_var_rule = lib.plot_pdf_rule(dgfor,fdate=forecast_based_on_date,q_low=lt, q_high=ut,ttle = ttle)






###############################################################################
#%% Below are dynamic over a time
###############################################################################

###############################################################################
#%% Conditional FX Volatility Over Time Satrting from a specific date
###############################################################################
# Style
sns.set(style='white', font_scale=2, palette='deep', font='serif')

# Plot
dgf.plot_in_cond_vol(start_date=None, #This can be None or dynamic_start
                     title='')
# Save the figure
cv_f = os.path.join('output', 'step004b_conditional_vol_plot.pdf')
plt.savefig(cv_f, bbox_inches='tight')
cv_f = os.path.join('output', 'step004b_conditional_vol_plot.png')
plt.savefig(cv_f)
plt.show()

# Create HTML version
fig_conditional_vol_plot = lib.plot_in_cond_vol(dgf, title='')



###############################################################################
### Drawing this plot takes super long time
#%% Joyplot Conditional Density Over Time Satrting from a specific date
###############################################################################
# Style
sns.set(style='white', font_scale=2, palette='deep', font='serif') 

if jp_out_sample == False:
    # Please a date with all independent var present
    dgfor_dynamic = dgf.forecast(dynamic_start, horizon=1)
else:
    # Fit the model
    dgf_dynamic = dg.fit(last_obs = dynamic_start)
    # Please a date with all independent var present
    dgfor_dynamic = dgf_dynamic.forecast(dynamic_start, horizon=1)

# Plot
dgfor_dynamic.joyplot_out(
    title='', # You can customize your plot title
    xlabel='',
    label_drop=5, # This param determines the inverval of y axis tick
    # xlimits_t=(-250, 250) # This param set the x tick limits
    )



# Save the figure
joyplot_f = os.path.join('output', 'step004b_joyplot.pdf')
plt.savefig(joyplot_f)

# png
joyplot_f = os.path.join('output', 'step004b_joyplot.png')
plt.savefig(joyplot_f,dpi = 1500)
fig_joyplot = imfplotly.Image(joyplot_f, text='Ridge plot',height = 800,
                      center=False, width=1300)
plt.show()


###############################################################################
#%% Fanchart Over Time Satrting from a specific date
###############################################################################
# Style
sns.set(style='white', font_scale=2, palette='deep', font='serif') 

if fc_out_sample == False:
    # Please a date with all independent var present
    dgfor_dynamic = dgf.forecast(dynamic_start, horizon=1)
else:
    # Fit the model
    dgf_dynamic = dg.fit(last_obs = dynamic_start)
    dgfor_dynamic = dgf_dynamic.forecast(dynamic_start, horizon=1)

# Plot
dgfor_dynamic.plot_fan_chart(xticks_freq=10, title='Fan chart of predictive FX log returns \n'
                     '( 5, 10, 25,50, 75, 90, 95th conditional quantiles)')
plt.ylabel('Pips')

# Save the figure
fanchart_f = os.path.join('output', 'step004b_fanchart.pdf')
plt.savefig(fanchart_f, bbox_inches='tight')
fanchart_f = os.path.join('output', 'step004b_fanchart.png')
plt.savefig(fanchart_f)
plt.show()

# Create HTML version
fig_fanchart = lib.plot_fan_chart(dgfor_dynamic,
                         xticks_freq=35,
                         ylabel='Pips',
                         title='Fan chart of predictive FX log returns \n'
                         '(5, 10, 25, 50, 75, 90, 95th conditional quantiles)')

###############################################################################
#%% Conditional CDF
###############################################################################
# Style
sns.set(style='white', font_scale=2, palette='deep', font='serif') 

if cd_out_sample == False:
    # Please a date with all independent var present
    dgfor_dynamic = dgf.forecast(dynamic_start, horizon=1)
else:
    # Fit the model
    dgf_dynamic = dg.fit(last_obs = dynamic_start)
    dgfor_dynamic = dgf_dynamic.forecast(dynamic_start, horizon=1)


# Plot
dgfor_dynamic.plot_conditional_cdf(q_low=lt, q_high=ut, size=300, title='', ylabel='Quantiles')

# Save the figure
cond_cdf_f = os.path.join('output', 'step004b_conditional_cdf.pdf')
plt.savefig(cond_cdf_f, bbox_inches='tight')
cond_cdf_f = os.path.join('output', 'step004b_conditional_cdf.png')
plt.savefig(cond_cdf_f)
plt.show()

# Create HTML version of conditional CDF
fig_conditional_CDF = lib.plot_conditional_cdf(dgfor_dynamic,
                               q_low=lt, q_high=ut, size=300, title='', ylabel='Quantiles')
###############################################################################
#%% Conditional VaR Exceedance
###############################################################################
sns.set(style='white', font_scale=2, palette='deep', font='serif') 

if cdv_out_sample == False:
    # Please a date with all independent var present
    dgfor_dynamic = dgf.forecast(dynamic_start, horizon=1)
else:
    # Fit the model
    dgf_dynamic = dg.fit(last_obs = dynamic_start)
    dgfor_dynamic = dgf_dynamic.forecast(dynamic_start, horizon=1)

# Plot
dgfor_dynamic .plot_var_exceedance(qv_l=[lt, ut], 
                          title_1= (f'Log Returns and Conditional VaR Exceedance at {lt*2*100} Percent'
                        f' \n (green square: below VaR {lt*100} percent, red dot: above VaR {ut*100}  percent)'),
                          title_2='Corresponding FX level',
                          swap_color=True, 
                          size=300)

# Save the figure
cond_exc_f = os.path.join('output', 'step004b_conditional_exceedance.pdf')
plt.savefig(cond_exc_f, bbox_inches='tight')
cond_exc_f = os.path.join('output', 'step004b_conditional_exceedance.png')
plt.savefig(cond_exc_f)
plt.show()



# Create HTML version later
title_1= 'Log Returns and Conditional VaR Exceedance'
title_2='Corresponding FX level'
fig_Cond_exceedance = lib.plot_var_exceedance(dgfor_dynamic,qv_l=[lt, ut],y1='Below', 
                                              y2='Above',lineval = 'true_val', title = title_1)
fig_Cond_exceedance2 = lib.plot_var_exceedance(dgfor_dynamic,qv_l=[lt, ut],y1='Level Below',margin_bottom = 100,
                                               y2='Level Above',lineval = 'FX level', title = title_2)

###############################################################################
#%% Save important variables
###############################################################################
import shelve

filename='intermediary results/step004b_crucial_results.out'
my_shelf = shelve.open(filename,'n') 

for key in ['fig_Cond_exceedance','fig_Cond_exceedance2','fig_conditional_CDF','fig_joyplot','fig_conditional_vol_plot','fig_var_rule',
            'fig_pit','forecast_based_on_dateb','target_date_date', 'target_dateb', 'joyplot_f','fig_fanchart','cond_exc_f','lt','ut','dynamic_start',
            'cdv_out_sample','cd_out_sample','fc_out_sample','jp_out_sample']:
    try:
        my_shelf[key] = globals()[key]
    except TypeError:
        #
        # __builtins__, my_shelf, and imported modules can not be shelved.
        #
        print('ERROR shelving: {0}'.format(key))
