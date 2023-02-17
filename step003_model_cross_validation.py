# -*- coding: utf-8 -*-
"""
Created on Sun Jul 31 20:34:53 2022

@author: ZChen4

This script enables cross-validation for provided specifications
"""
###############################################################################
#%% Modules
###############################################################################
# System paths
import os, sys
sys.path.append(os.path.abspath('modules'))
import scipy

# Global modules
import importlib                                        # Operating system
import pandas as pd                                     # Dataframes
import numpy as np                                      # Numeric Python
import arch                                             # ARCH/GARCH models
from scipy import stats                                 # Statistics 
import math 
from scipy.stats import iqr
import itertools

# ARCH package functional imports
from arch.univariate import (ARCH, GARCH, EGARCH, EWMAVariance, # Vol process
                             RiskMetrics2006, ConstantVariance) 
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

# Import data treatment
import step002_data_treatment as dat_tm

###############################################################################
#%% Local functions
###############################################################################
# Function to calculate RMSE
def rmse_cal(resid_df):
    resid_df = resid_df.dropna()
    return(math.sqrt(np.nansum(resid_df*resid_df)/len(resid_df)))

# Function to calculate MAE
def mae_cal(resid_df):
    resid_df = resid_df.dropna()
    return(np.nansum(abs(resid_df))/len(resid_df))

# Function to split time series into k folds
def time_series_rolling_split(df, k_fold=10, window_fold = 5, test_fold = 1):
    iteration_n= int(k_fold - window_fold - test_fold +1)
    data_length = len(df)
    fold_size = int(data_length//k_fold)
    print(f'There will be {iteration_n} iterations. And 1 fold contains {fold_size} data points')
    
    start= data_length%k_fold
    data_l = list()
    for i in range(0, iteration_n):
        df_train_index = df.iloc[start:(start+fold_size*window_fold),:]
        df_test_index = df.iloc[(start+fold_size*window_fold):(start+fold_size*window_fold+test_fold*fold_size),:]
        start = start+fold_size
        data_l.append({'train':df_train_index, 'test':df_test_index})
    return(data_l,fold_size,iteration_n)

# Function to check whether a series remains constant all the time
def non_all_zero_date(df, var_l):
    exo_df = df[var_l].dropna()
    check_l = [col_n for col_n in exo_df.columns.tolist() if len(exo_df[col_n].unique())==1]
    if len(check_l)!=0:
        print(f'Please remove the following columns, beasue their values remain unchanged in the dataset:\n{check_l}')
        return(-1)
    else:
       exo_diff_df = exo_df.diff().dropna()
       m = exo_diff_df.ne(0).idxmax()
       first_non_zero = pd.DataFrame(dict(pos=m))
       return(max(first_non_zero['pos']))



###############################################################################
#%% Configuration
###############################################################################
# Start of series
start = '2000-01-01'
# start = '2013-01-21'

# End of series
end = None

# AR lag in mean model
lag_ar = [1]
# lag_ar = [1, 2, 3]

# For noncrossvalidated out-of-sample testing
# Please set a seperation points
# This point and dates after will form the testing set
# Dates before this point will form the training set
last_obs_mod = '2022-09-30'


# For cross validation, you need to provide following parameters
# So that the data can be split into various training and testing sets
# How many folds do you want to sepearte the data into
k_fold = 20
# How many folds do you want to include in the very first training set
window_fold = 10
# How many folds do you want to be in the testing set
test_fold = 1 

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
#%% Configuration: Model specification
###############################################################################

# Generate all possible combination
# item = ['VIX fd', 'Bid ask abs', 'High low abs', 'Oil prices fd',
#         'Interbank spread', 'EURUSD log returns']

# exo_spec_l = list()
# for i in range(0, len(item)+1):
#    temp = [list(x) for x in itertools.combinations(item, i)]
#    for j in temp:
#        exo_spec_l.append(j) 

# # Give the above models more readable names
# exo_labels_l = [f'Model {num}' for num in range(1, len(exo_spec_l)+1)]

# ###### Don't change the following. The following is for NAIVE
# naive_config = ['Model 1', 'Constant', 'Normal']
# ###### Don't change the following. The following is for NAIVE



microstructure = ['Bid ask abs', 'High low abs']

cip = microstructure + ['Interbank spread']

usdmove = cip + ['EURUSD log returns']

vix = usdmove + ['VIX fd']

baseline =  vix + ['Oil prices fd']


###### Don't change this empty. This is for naive
empty = []
###### Don't change this empty. This is for naive

# List of exogenous variables model
exo_spec_l = [empty, microstructure, cip, usdmove, vix, baseline]
# Give the above models more readable names. Please put the name in the correct order
exo_labels_l =['Empty', 'Microstructure','CIP', 'Dollar move', 'Risk Appetite', 
                'Baseline']

###### Don't change the following. The following is for NAIVE
# Determine which specification is naive
naive_config = ['Empty', 'Constant', 'Normal']
###### Don't change the following. The following is for NAIVE

###############################################################################
## Below are complete list of volitility and distribution models
## You don't need to change the following unless you want to delete some models
###############################################################################
# List of volitility model
vol_spec_l = [ConstantVariance(), ARCH(1), EGARCH(1,1,1), GARCH(1), GARCH(1,1), EWMAVariance(None), RiskMetrics2006()]
# Give the above models more readable names
vol_labels_l = ['Constant', 'ARCH', 'EGARCH', 'GARCH', 'gjrGARCH', 'EWMA', 'RiskMetric']

# List of error distribution
errdist_l = [Normal(), StudentsT(), SkewStudent(), GeneralizedError()]
# Give the above models more readable names
errdist_labels_l = ['Normal', 'StudentT', 'SkewStudent', 'GeneralizedError']

all_var_l = list(set(sum(exo_spec_l, [])))

###############################################################################
#%% No Cross Validation: will gerenrate non crossvalidated in and out of sample testing results
###############################################################################
df_short =  df[all_var_l+['FX log returns', 'FX level']].dropna().sort_index()
last_date_short = max(df_short.index)

vol_dist_spec_l = list()

for vol_label, vol_model in zip(vol_labels_l, vol_spec_l): # Loop over volitility models
    for err_label, dist in zip(errdist_labels_l, errdist_l): # Loop over distribution models
        exo_specification_tables_l = list()
        exo_specification_tables_short_l = list()
        try:
            for exo_label, exo_model in zip(exo_labels_l, exo_spec_l): # Loof over exogenous models
                dgm = DistGARCH(depvar_str='FX log returns', # Name of dep var
                                data=df, # Dataframe to work on
                                level_str='FX level', # Name of level dep var
                                exog_l=exo_model, # Exogenous variable models
                                lags_l=lag_ar, # Lag for AR term
                                vol_model= vol_model, # Volitility model
                                dist_family=dist # Distribution innovation
                                )
                
                # This is an in-sample fit. Because no last observation was set
                dgfit = dgm.fit()
                
                # Generate the tables
                var_d = dict()
                for i in lag_ar:
                    var_d[f'FX l...rns[{i}]'] = f'Lag {i} FX log returns'
                lag_name_l = list(var_d.values())
                sumtable = dgfit.summary_table(model_name=exo_label+' ['+vol_label+', '+err_label+']', var_d=var_d,
                                                print_pval=True)
                sumtable_short = dgfit.summary_table(model_name=exo_label+' ['+vol_label+', '+err_label+']', var_d=var_d,
                                                      print_pval=False)
                
                # This is the in-sample forecast. Forecasting from the start to the end
                dgfor = dgfit.forecast(min(dgfit.df.index), horizon=1)
                # Get the forecasting table with other important statistics
                predict_df = dgfor.dfor
                
                # In-sample conditional mean and its RMSE/MAE
                mean_df = predict_df[['true_val', 'cond_mean']].copy()
                mean_df['mean_forecast']  = mean_df['cond_mean'].shift(1)
                mean_df['mean_resid'] = mean_df['true_val'] - mean_df['mean_forecast']
                # In-sample conditional RMSE
                mean_rmse_score = rmse_cal(mean_df['mean_resid'])
                sumtable_short.loc['In-sample RMSE (COND MEAN)'] = mean_rmse_score
                # In-sample conditional MAE
                mean_mae_score = mae_cal(mean_df['mean_resid'])
                sumtable_short.loc['In-sample MAE (COND MEAN)'] = mean_mae_score
                
                # In-sample conditional density and MIS
                mis_df =  predict_df.copy()
                mis_df['is'] = (mis_df['cond_quant_0.975']-mis_df['cond_quant_0.025'])+(2/(1-0.95))*(mis_df['cond_quant_0.025']-mis_df['true_val'])*(mis_df['true_val']<mis_df['cond_quant_0.025'])+(2/(1-0.95))*(mis_df['true_val']-mis_df['cond_quant_0.975'])*(mis_df['true_val']>mis_df['cond_quant_0.975'])
                mis_score = np.nanmean(mis_df['is'])
                sumtable_short.loc['In-sample MIS'] = mis_score
                
                # In-sample density KS testing
                ks_stats = stats.kstest(predict_df['pit'].dropna(), 'uniform').statistic
                sumtable_short.loc['In-sample KS stat'] = ks_stats
                ks_pval = stats.kstest(predict_df['pit'].dropna(), 'uniform').pvalue
                sumtable_short.loc['In-sample KS pvalue'] = ks_pval
                sumtable_short.loc['In-sample KS status'] = 'Pass' if ks_pval>0.05 else 'Fail'
                
                
                # Following is out of sample testing
                # Set a spepration date for training and testing set
                dg_os_fit = dgm.fit(last_obs = last_obs_mod) 
                # Forecast from the first date of testing set
                predict_os_df = dg_os_fit.forecast(last_obs_mod, horizon=1).dfor
                predict_os_df = predict_os_df.loc[:last_date_short]
                
                # Out-sample conditional mean and its RMSE/MAE
                mean_os_df = predict_os_df[['true_val', 'cond_mean']].copy()
                mean_os_df['mean_forecast']  = mean_os_df['cond_mean'].shift(1)
                mean_os_df['mean_resid'] = mean_os_df['true_val'] - mean_os_df['mean_forecast']
                # Out-sample conditional mean RMSE
                mean_os_rmse_score = rmse_cal(mean_os_df['mean_resid'])
                sumtable_short.loc['Out-sample RMSE (COND MEAN)'] = mean_os_rmse_score
                # Out-sample conditional mean MAE
                mean_os_mae_score = mae_cal(mean_os_df['mean_resid'])
                sumtable_short.loc['Out-sample MAE (COND MEAN)'] = mean_os_mae_score
                
                # Out-sample conditional density and MIS
                mis_os_df =  predict_os_df.copy()
                mis_os_df['is'] = (mis_os_df['cond_quant_0.975']-mis_os_df['cond_quant_0.025'])+(2/(1-0.95))*(mis_os_df['cond_quant_0.025']-mis_os_df['true_val'])*(mis_os_df['true_val']<mis_os_df['cond_quant_0.025'])+(2/(1-0.95))*(mis_os_df['true_val']-mis_os_df['cond_quant_0.975'])*(mis_os_df['true_val']>mis_os_df['cond_quant_0.975'])
                mis_os_score = np.nanmean(mis_os_df['is'])
                sumtable_short.loc['Out-sample MIS'] = mis_os_score
                
                # Out-sample density KS testing
                ks_stats_os = stats.kstest(predict_os_df['pit'].dropna(), 'uniform').statistic
                sumtable_short.loc['Out-sample KS stat'] = ks_stats_os
                ks_pval_os = stats.kstest(predict_os_df['pit'].dropna(), 'uniform').pvalue
                sumtable_short.loc['Out-sample KS pvalue'] = ks_pval_os
                sumtable_short.loc['Out-sample KS status'] = 'Pass' if ks_pval_os>0.05 else 'Fail'
                
                exo_specification_tables_l.append(sumtable)
                exo_specification_tables_short_l.append(sumtable_short)
                
            # Merge all the summary tables
            exo_dsum = pd.concat(exo_specification_tables_l, axis=1)
            exo_dsum_short = pd.concat(exo_specification_tables_short_l, axis=1)
            exo_dsum_short = exo_dsum_short.reindex(['In-sample RMSE (COND MEAN)', 'In-sample MAE (COND MEAN)', 
                                                     'In-sample MIS', 'In-sample KS stat', 'In-sample KS pvalue', 'In-sample KS status', 
                                                     'Out-sample RMSE (COND MEAN)', 'Out-sample MAE (COND MEAN)', 'Out-sample MIS', 
                                                     'Out-sample KS stat','Out-sample KS pvalue','Out-sample KS status']+
                                                      lag_name_l + all_var_l + ['R2','R2 adjusted', 'Intercept', 'Alpa', 'Beta', 'Lambda','Nu','Omega', 'Eta',
                                                      'lam', 'Number of observations'])
            vol_dist_spec_l.append(exo_dsum_short)
        except:
            model_name=exo_label+' ['+vol_label+', '+err_label+']'
            print(f'Error in {model_name}')
            sys.exit(1)
    
all_comb_t = pd.concat(vol_dist_spec_l, axis=1)

# Merge all the summary tables
all_comb_t.to_excel('output/step003_non_cross_validation_performace_table.xlsx')

###############################################################################
#%% With Cross Validation
###############################################################################
## Splitting and checking
# Put the datset into the spliter to get training and testing set for cross validartion
split_df,fold_size_out,iteration_n_out = time_series_rolling_split(df_short , k_fold, window_fold, test_fold)

# Check whether there is any series that is constant from the begining to the end for each training set
skip_det_date = non_all_zero_date(df_short, all_var_l)
if skip_det_date!=-1:
    for i in split_df:
        last_obs = max(i['train'].index)
        if skip_det_date>last_obs:
            print('Please regenerte the training dataset. Some variables remain unchanged in the tarining dataset')
            

#%% Running cross validation
vol_dist_spec_cv_l = list()

for vol_label, vol_model in zip(vol_labels_l, vol_spec_l): # Loop for volitility model
    for err_label, dist in zip(errdist_labels_l, errdist_l): # Loop for error distribution model
        exo_spec_cv_l = list() 
        for exo_label, exo_model in zip(exo_labels_l, exo_spec_l): # Loop for exogenous variabales
            cv_all_l = list()
            for split in split_df: # Loop over different training set
                model_name=exo_label+' ['+vol_label+', '+err_label+']'
                df_cv = pd.concat(split)
                df_cv = df_cv.droplevel(0)
                dg_cv = DistGARCH(depvar_str='FX log returns', # Name of dep var
                                data=df_cv, # Dataframe to work on
                                level_str='FX level', # Name of level dep var
                                exog_l=exo_model,  # Exogenous variable models
                                lags_l=lag_ar, # Lag for AR term
                                vol_model= vol_model, # Volatility model
                                dist_family=dist # Distribution innovation
                                ) 
                
                # Get the separation point between training and testing set
                last_obs_mod_cv = min(split['test'].index)
                # Set the separation point as last observation [excl.]
                dg_os_fit = dg_cv.fit(last_obs = last_obs_mod_cv)
                
                # Fit from the seperation point
                predict_os_df = dg_os_fit.forecast(last_obs_mod_cv, horizon=1).dfor
                
                # Cross validation conditional mean: RMSE and MAE
                mean_os_df = predict_os_df[['true_val', 'cond_mean']].copy()
                mean_os_df['mean_forecast']  = mean_os_df['cond_mean'].shift(1)
                mean_os_df['mean_resid'] = mean_os_df['true_val'] - mean_os_df['mean_forecast']
                mean_os_rmse_score = rmse_cal(mean_os_df['mean_resid'])
                mean_os_mae_score = mae_cal(mean_os_df['mean_resid'])
                cv_df = pd.DataFrame(columns=[model_name])
                cv_df.loc['Cross Validation Out-sample RMSE (COND MEAN)'] = mean_os_rmse_score
                cv_df.loc['Cross Validation Out-sample MAE (COND MEAN)'] = mean_os_mae_score
                
                # Cross validation conditional density: MIS
                mis_os_df =  predict_os_df.copy()
                mis_os_df['is'] = (mis_os_df['cond_quant_0.975']-mis_os_df['cond_quant_0.025'])+(2/(1-0.95))*(mis_os_df['cond_quant_0.025']-mis_os_df['true_val'])*(mis_os_df['true_val']<mis_os_df['cond_quant_0.025'])+(2/(1-0.95))*(mis_os_df['true_val']-mis_os_df['cond_quant_0.975'])*(mis_os_df['true_val']>mis_os_df['cond_quant_0.975'])
                mis_os_score = np.nanmean(mis_os_df['is'])
                cv_df.loc['Cross Validation Out-sample MIS'] = mis_os_score
                
                # Cross validation conditional density: KS test
                ks_stats_os = stats.kstest(predict_os_df['pit'].dropna(), 'uniform').statistic
                ks_pval_os = stats.kstest(predict_os_df['pit'].dropna(), 'uniform').pvalue
                cv_df.loc['Cross Validation Out-sample KS stat'] = ks_stats_os
                cv_df.loc['Cross Validation Out-sample KS pvalue'] = ks_pval_os
                cv_df.loc['Cross Validation Out-sample KS Pass Pct'] = 1 if ks_pval_os>0.05 else 0
                
                cv_all_l.append(cv_df)
            
            # Merge all summary table
            cv_all_df = pd.concat(cv_all_l, axis=1)
            cv_avg_single_df = pd.DataFrame(cv_all_df.mean(axis=1))
            cv_avg_single_df.columns=[model_name]
            exo_spec_cv_l.append(cv_avg_single_df)
        exo_spec_cv_df = pd.concat(exo_spec_cv_l, axis=1)
        vol_dist_spec_cv_l.append(exo_spec_cv_df)
    
all_comb_cv_t = pd.concat(vol_dist_spec_cv_l, axis=1)


# Save the table
all_comb_cv_t.to_excel('output/step003_cross_validation_performace_table.xlsx')

###############################################################################
#%% Merge and save non cross validation and cross validation results
###############################################################################
all_comb_cv_final = pd.concat([all_comb_t, all_comb_cv_t])

all_comb_cv_final.to_excel('output/step003_performace_table_all_in_one.xlsx')











###############################################################################
#%% Construct the combination pool and calculate the weight for conditional mean
###############################################################################
# Get mean RMSE
mean_table = all_comb_cv_final.loc[['Cross Validation Out-sample RMSE (COND MEAN)'],:].copy().transpose().sort_values('Cross Validation Out-sample RMSE (COND MEAN)')

# Calculate selection threshold
th_list = list()
for i in range(0, len(mean_table)):
    df_th = mean_table.iloc[0:i+1,:].copy()
    mean_threshold = np.quantile(df_th,0.75) + 1.5*iqr(df_th)
    th_list.append(mean_threshold)
mean_table['Threshold'] =  th_list   

# Filter out models that exceed the threshold
mean_table['Included'] = (mean_table['Cross Validation Out-sample RMSE (COND MEAN)']<=mean_table['Threshold'])
if len(mean_table['Included'].unique()) == 1:
    mean_selected_table = mean_table.copy()
else:
    first_false_index = mean_table['Included'].reset_index(drop=True).eq(False).idxmax()
    mean_selected_table = mean_table.iloc[0:first_false_index,:].copy()

# Calculate the weight for the combination pool
mean_selected_sum = (1/mean_selected_table['Cross Validation Out-sample RMSE (COND MEAN)']).sum()
mean_selected_table['Weight'] = (1/mean_selected_table['Cross Validation Out-sample RMSE (COND MEAN)'])/mean_selected_sum

# Store sepcification info of the combination pool 
mean_selected_spec_list = list()
for i in mean_selected_table.index.tolist():
    split_list = i.split('[')
    vod_dist_l = split_list[1].rstrip(']').split(', ')
    mean_selected_spec_list.append([split_list[0].strip()]+vod_dist_l)

###############################################################################
#%% Construct the combination pool and calculate the weight for conditional density
###############################################################################
# Get density MIS
density_table = all_comb_cv_final.loc[['Cross Validation Out-sample MIS'],:].copy().transpose().sort_values('Cross Validation Out-sample MIS')

# Calculate selection threshold
density_th_list = list()
for i in range(0, len(density_table)):
    df_th_density = density_table.iloc[0:i+1,:].copy()
    density_threshold = np.quantile(df_th_density,0.75) + 1.5*iqr(df_th_density)
    density_th_list.append(density_threshold)
density_table['Threshold'] =  density_th_list   

# Filter out models that exceed the threshold
density_table['Included'] = (density_table['Cross Validation Out-sample MIS']<=density_table['Threshold'])
if len(density_table['Included'].unique()) == 1:
    density_selected_table = density_table.copy()
else:
    density_first_false_index = density_table['Included'].reset_index(drop=True).eq(False).idxmax()
    density_selected_table = density_table.iloc[0:density_first_false_index,:].copy()

# Calculate the weight for the combination pool
density_selected_sum = (1/density_selected_table['Cross Validation Out-sample MIS']).sum()
density_selected_table['Weight'] = (1/density_selected_table['Cross Validation Out-sample MIS'])/density_selected_sum

# Store sepcification info of the combination pool
density_selected_spec_list = list()
for i in density_selected_table.index.tolist():
    split_list = i.split('[')
    vod_dist_l = split_list[1].rstrip(']').split(', ')
    density_selected_spec_list.append([split_list[0].strip()]+vod_dist_l)

###############################################################################
#%% Combined list for slected mean and density models
###############################################################################
selected_both_spec_raw_l = list(set(mean_selected_table.index.tolist()).union(set(density_selected_table.index.tolist())))

selected_both_spec_l = list()     
for i in selected_both_spec_raw_l:
    split_list = i.split('[')
    vod_dist_l = split_list[1].rstrip(']').split(', ')
    selected_both_spec_l.append([split_list[0].strip()]+vod_dist_l)

if naive_config not in selected_both_spec_l:
    selected_both_spec_l.append(naive_config)

# NAIVE model
new_naive_config = naive_config[0]+' ['+naive_config[1]+', '+naive_config[2]+']'
naive_rmse = all_comb_cv_final.loc['Cross Validation Out-sample RMSE (COND MEAN)',new_naive_config]
naive_mis = all_comb_cv_final.loc['Cross Validation Out-sample MIS',new_naive_config]       


###############################################################################
#%% Save important variables
###############################################################################
import shelve

exo_dict = dict(zip(exo_labels_l,exo_spec_l))
vol_dict = dict(zip(vol_labels_l, vol_spec_l))
errdist_dict = dict(zip(errdist_labels_l, errdist_l))

filename='intermediary results/step003_crucial_results.out'
my_shelf = shelve.open(filename,'n') 
for key in ['lag_ar','all_var_l', 'naive_config', 'new_naive_config','exo_labels_l', 'exo_spec_l', 
            'vol_labels_l', 'vol_spec_l', 'exo_dict', 'vol_dict', 'errdist_dict',
            'errdist_labels_l', 'errdist_l', 'selected_both_spec_l', 
            'mean_selected_table', 'density_selected_table','k_fold','fold_size_out',
            'window_fold','test_fold','iteration_n_out', 'naive_rmse', 'naive_mis']:
    try:
        my_shelf[key] = globals()[key]
    except TypeError:
        #
        # __builtins__, my_shelf, and imported modules can not be shelved.
        #
        print('ERROR shelving: {0}'.format(key))

mean_selected_table.to_csv('output/step003_combination_pool_for_mean.csv')
density_selected_table.to_csv('output/step003_combination_pool_for_density.csv')