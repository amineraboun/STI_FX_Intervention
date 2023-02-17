'''
2022-9-03 Adeleke Adeyemi
Create all HTML outputs and link together.

****************************************************************************
You need imfplotly placed in site-packages
****************************************************************************
'''
###############################################################################
#%% There is one block only in this cript. So shift enter once will run the whole code
###############################################################################

from collections import OrderedDict

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.distributions.empirical_distribution import ECDF
import importlib                                        # Operating system
import os
import sys
sys.path.append(os.path.abspath('modules'))
import imfplotly
import matplotlib.pyplot as plt
import matplotlib.image as img
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy.stats as st
from modules.distGARCH import closest

###############################################################################
#Load in important results from step003
###############################################################################
import shelve

my_shelf = shelve.open('intermediary results/step004B_crucial_results.out')
for key in my_shelf:
    globals()[key]=my_shelf[key]
my_shelf.close()



my_shelf = shelve.open('intermediary results/step004A_crucial_results.out')
for key in my_shelf:
    globals()[key]=my_shelf[key]
my_shelf.close()

my_shelf = shelve.open('intermediary results/step003_crucial_results.out')
for key in my_shelf:
    globals()[key]=my_shelf[key]
my_shelf.close()

my_shelf = shelve.open('intermediary results/step000_crucial_results.out')
for key in my_shelf:
    globals()[key]=my_shelf[key]
my_shelf.close()


masterfilename = 'master.html'
backlink = {'Back to index' : masterfilename}
links = dict()
###############################################################################
###############################################################################

#--------------------------------------------------------------------
# Descriptive report
#--------------------------------------------------------------------
###############################################################################
###############################################################################

object_desc = []
df_des = pd.read_csv('output/step000_df_des.csv', index_col= 'date')

# -----------------------------------------------------
# Create HTML version of description plot
title = imfplotly.Heading1('Descriptive Summary on Historical FX and Intervention')
object_desc.append(title)





figtitle = 'Historical FX Level'
linecols = 'FX level'
ytitle_returns = f'{currency_pair}'
dict_colors = {linecols : {'color' : 'Blue',
                                'width' : 4,
                                'dash'  : None}}

fig = imfplotly.create_fig(df_des,
                           linecols='FX level',
                           dict_colors=dict_colors,
                           ytitle=ytitle_returns,
                           figtitle=figtitle,
                           bar_opacity=0.7)
object_desc.append(fig)



figtitle = 'Historical FX Returns'
linecols = 'FX log returns'
ytitle_returns = 'Bps'
dict_colors = {linecols : {'color' : 'Green',
                                'width' : 4,
                                'dash'  : None}}

fig = imfplotly.create_fig(df_des,
                           linecols=linecols,
                           dict_colors=dict_colors,
                           ytitle=ytitle_returns,
                           figtitle=figtitle,
                           bar_opacity=0.7)
object_desc.append(fig)




        
_fig, _ax = plt.subplots()
ax = sns.histplot(df_des['FX log returns'], kde=True, label='KDE',bins =100, ax=_ax)
plt.close()
x1, y1 = ax.get_lines()[0].get_data()
x2 = [p.get_x() + p.get_width()/2. for p in ax.patches]
y2 = [p.get_height() for p in ax.patches]

        # Create DataFrames
cols = ['KDE', 'KDE hist']
_df1 = pd.DataFrame({'x' : x1, cols[0] : y1}).set_index('x')
_df2 = pd.DataFrame({'x' : x2, cols[1] : y2}).set_index('x')
 

figtitle = 'Kernel Density Estimation of the Historical FX Returns'
ytitle_returns = 'Density'       
dict_colors = {cols[0] : {'color' : 'blue'},
               cols[1] : {'color' : 'blue'}}
    
#Add text to the chart mode = 0.39,2.5% =-125.27,97.5%=131.13
_vline_mode = imfplotly.VLine(x=0.39, text='mode',font_size = 24)
_vline_l = imfplotly.VLine(x=-125.27, text='2.5%',font_size = 24)
_vline_u = imfplotly.VLine(x=131.13, text='97.5%',font_size = 24)

dict_markers = {col : {'opacity' : 0, 'size' : 0} for col in cols}
    
    # Plot density distribution
fig = imfplotly.create_fig(_df1, linecols=cols[0],xtitle ='FX log return',ytitle ='Density',
                              dict_colors=dict_colors,                               
                              vlines=[_vline_mode,_vline_l,_vline_u],
                              dict_markers=dict_markers,
                              figtitle = 'Kernel Density Estimation of the Historical FX Log Returns')
    
    # KDE histogram or best_dist
fig = imfplotly.add_bars(_df2, cols[1],
                         dict_colors=dict_colors,
                         fig=fig)
   
object_desc.append(fig)

  

# #4th plots

# raw_data_cdf_df = df_des[['FX log returns']].copy().dropna().sort_index()
# kde_df_raw = df_des['FX log returns'].copy().dropna()
# kde = st.gaussian_kde(kde_df_raw)
# cdf_kde = np.vectorize(lambda x: kde.integrate_box_1d(-np.inf, x))

# raw_data_cdf_df['CDF'] = cdf_kde(raw_data_cdf_df)

# dict_markers = {'CDF' : {'opacity' : 0.5, 'size' : 0.5}}
# dict_colors = {'CDF':{'color': 'mediumslateblue'}}                               
# _hline_low = imfplotly.HLine(y=0.025)
# _hline_up  = imfplotly.HLine(y=0.975)
# ytitle_returns = 'Quantile'       
# figtitle =  'Unconditional CDF with USD Intervention'

# fig = imfplotly.create_fig(raw_data_cdf_df, linecols='CDF',dict_markers=dict_markers,dict_colors=dict_colors,
#                            hlines= [_hline_low,_hline_up],ytitle=ytitle_returns,
#                            figtitle=figtitle)
# sell_des_df = df_des[['ivt_usd_sell_dummy']].copy().dropna()
# raw_data_cdf_df = raw_data_cdf_df.merge(sell_des_df, left_index=True, right_index=True, how='right')
# raw_data_cdf_df['Sell']=np.where(raw_data_cdf_df['ivt_usd_sell_dummy'] == 0,np.nan,raw_data_cdf_df['CDF'])


# buy_des_df = df_des[['ivt_usd_buy_dummy']].copy().dropna()
    
# raw_data_cdf_df = raw_data_cdf_df.merge(buy_des_df, left_index=True, right_index=True, how='right')

# raw_data_cdf_df['Buy']=np.where(raw_data_cdf_df['ivt_usd_buy_dummy'] == 0,np.nan,raw_data_cdf_df['CDF'])


# dict_colors = {'Buy' : {'color' : 'red','width' : 0},
#                "Sell" : {'color' : 'green','width' : 0}}

# dict_markers = {'Buy' : {'symbol' : 'triangle-down', 'size' : 10},
#                 'Sell' : {'symbol' : 'circle', 'size' : 10}}

    



# fig = imfplotly.add_lines(raw_data_cdf_df, linecols= ['Buy','Sell'],fig = fig,dict_colors=dict_colors,dict_markers = dict_markers)

# object_desc.append(fig)


# text = 'Note: The unconditional CDF is derived from the KDE'
# markdown = imfplotly.Markdown(text)
# object_desc.append(markdown)







title = "Descriptive report"


imfplotly.create_html('html_report/desc.html', object_desc,
                          links=backlink, # add link back to master file
                          show=False)
   
 # Add to links
links[title] = "desc.html"

#

###############################################################################
###############################################################################

#--------------------------------------------------------------------
# Cross validation report
#--------------------------------------------------------------------
###############################################################################
###############################################################################


objects_cv = []
forecasted_density_w_df = pd.read_csv('intermediary results/step004a_forecasted_density_w_df.csv', index_col= 'Index')
forecasted_density_w_df_final = pd.read_csv('intermediary results/step004a_forecasted_density_w_df_final.csv', index_col= 'Index')

# Create HTML version of cross validation plot
title = imfplotly.Heading1('Cross Validation Report')
objects_cv.append(title)


text = (f' The cross-validation process starts with a subset of data for model training,' 
f' \n forecasts for a following period, and measuring the forecasting performance.'
f' \n The same forecasted period will then be added to the training set for the next iteration.')
markdown = imfplotly.Heading3(text,fontsize=14)
objects_cv.append(markdown)

            
text = (f'This cross-validation exercise has split data into {k_fold} folds. Each fold contains {fold_size_out} datapoints.'
        f'\n The starting training set includes {window_fold} folds. The testing set is fixed as {test_fold} fold(s) and there'
        f'\n are {iteration_n_out} iterations in total.')
markdown = imfplotly.Heading3(text,fontsize=14)
objects_cv.append(markdown)

fig = imfplotly.Image('intermediary results/cval.png', text='',center=False)
objects_cv.append(fig)


title = imfplotly.Heading1('Cross Validation for the Conditional Mean and Example on Model Combination', fontsize=20)
objects_cv.append(title)

text = (f'RMSE is used to measure the predictive performance of the models in terms of conditional mean. In total,'
        f'\n {len(mean_selected_table)} models are selected for model combination according to the thresholds*.')

markdown = imfplotly.Heading3(text,fontsize=14)
objects_cv.append(markdown)




forecasted_mean_w_df.rename(columns = {'Cross Validation Out-sample RMSE (COND MEAN)':'RMSE',
                          'weight_mean': 'Weighted Mean','cond_mean':'Conditional Mean','Weight':'Weight'}, inplace = True)

new_col_order = ['Conditional Mean', 'Weighted Mean', 'RMSE', 'Threshold', 'Weight']



forecasted_mean_w_df_table = forecasted_mean_w_df[new_col_order].astype(float)
#cols = [c for c in forecasted_mean_w_df_table.columns if c != 'Included']
table = imfplotly.create_bokeh_table(forecasted_mean_w_df_table, 
                                     dateindex=False, indexname='',prec=3,
                                     # index_font_color='red', index_font_size=24,
                                     nan_val='',row_height = 35,
                                     index_width=450, col_width=250,
                                     sortable=False)



objects_cv.append(table)
# Create space in between
#space = imfplotly.Space(2.5)
#objects_cv.append(space)


forecasted_mean_w_df.loc['Weighted Average'] = pd.Series(forecasted_mean_w_df['Weighted Mean'].copy().sum(), index=['Conditional Mean'])



xcl_df = forecasted_mean_w_df.index.isin(['Weighted Average'])

 
barcols = 'Conditional Mean'
figtitle = 'Conditional Mean'

fig = imfplotly.create_fig(forecasted_mean_w_df[xcl_df],
                            barcols = barcols,showlegend=False,linecols = None,
                           figtitle=figtitle,xfontsize=15,list_barcolors ='purple',
                           # Set area to True to get area chart
                           xangle=-90,xnticks=len(forecasted_mean_w_df)+1,height= 900,
                           bar_opacity=1,margin_bottom=300)

fig = imfplotly.add_bars(forecasted_mean_w_df[~xcl_df],
                           fig=fig, barcols = barcols,
                           # Set area to True to get area chart
                          opacity=1)



fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)
objects_cv.append(fig)





title = imfplotly.Heading1('Cross Validation for the Conditional Density and Example on Model Combination', fontsize=20)
objects_cv.append(title)

text = (f'MIS is used to measure the predictive performance of the models in terms of conditional density.'
        f'\nIn total {len(density_selected_table)} models are selected for model combination according to the thresholds*.')


markdown = imfplotly.Heading3(text,fontsize=14)
objects_cv.append(markdown)

cols = ['Cross Validation Out-sample MIS', 'Threshold','cond_quant_0.025', 'cond_quant_0.05','cond_quant_0.1',
        'cond_quant_0.25','cond_quant_0.5',  'cond_quant_0.75', 'cond_quant_0.9', 'cond_quant_0.95', 'cond_quant_0.975', 'Weight']
      
forecasted_density_w_df_tab = forecasted_density_w_df[cols]
forecasted_density_w_df_tab = forecasted_density_w_df_tab[cols]







forecasted_density_w_df_tab.rename({'Cross Validation Out-sample MIS':'MIS','cond_quant_0.025': '2.5%','cond_quant_0.05':'5%',
                                              'cond_quant_0.1': '10%','cond_quant_0.25':'25%','cond_quant_0.5': '50%','cond_quant_0.75':'75%',
                                              'cond_quant_0.9': '90%','cond_quant_0.95':'95%','cond_quant_0.975': '97.5%','Weight':'Weight'},
                                   axis=1, inplace = True)

cols =['2.5%', '5%', '10%', '25%', '50%', '75%', '90%','95%', '97.5%']
forecasted_density_w_df_plot = forecasted_density_w_df_tab[cols].copy()

table = imfplotly.create_bokeh_table(forecasted_density_w_df_tab, 
                                     dateindex=False, indexname='',prec=3,
                                     # index_font_color='red', index_font_size=24,
                                     nan_val='',row_height = 35,
                                     index_width=350, col_width=100,
                                     sortable=False)
objects_cv.append(table)
#space = imfplotly.Space(2.5)
#objects_cv.append(space)

cols = ['cond_quant_0.025', 'cond_quant_0.05','cond_quant_0.1','cond_quant_0.25','cond_quant_0.5',  'cond_quant_0.75', 
        'cond_quant_0.9', 'cond_quant_0.95', 'cond_quant_0.975']
   
forecasted_density_w_df_final_2 =  forecasted_density_w_df_final[cols].copy()


forecasted_density_w_df_final_2.rename(columns = {'cond_quant_0.025': '2.5%',
                                          'cond_quant_0.05':'5%','cond_quant_0.1': '10%','cond_quant_0.25':'25%',
                                          'cond_quant_0.5': '50%','cond_quant_0.75':'75%','cond_quant_0.9': '90%',
                                          'cond_quant_0.95':'95%','cond_quant_0.975': '97.5%'}, inplace = True)


forecasted_density_w_df_plot.loc['Weighted Combination'] = pd.Series(forecasted_density_w_df_final_2.sum().copy())

lisst = list(forecasted_density_w_df_final_2.index)
#collist = ['Weighted Combination']
collist = ['Weighted Combination']+lisst


#collist.append()

forecasted_density_w_df_plot=forecasted_density_w_df_plot.reindex(collist)
ttle = 'MIS Density'
t1 = f'Fan chart of predictive {figtitle}'
ttl = t1 + '\n 2.5, 5, 10, 25, 50, 75, 90, 95, 97.5 Conditional Quantiles'
ylabel = ''

# Create fig
linecols = ['2.5%','5%','10%','25%', '50%', '75%', '90%','95%','97.5%']
dict_colors = {'2.5%'    : {'color' : 'black', 'dash' : 'dash'},
                   '5%'   : {'color' : 'black', 'dash' : 'dot'},
                   '10%'   : {'color' : 'black', 'dash' : 'dashdot'},
                   '25%'   : {'color' : 'black', 'dash' : 'dash'},
                   '50%' : {'color' : 'black', 'width' : 2},
                   '75%'   : {'color' : 'black', 'dash' : 'dash'},
                   '95%'   : {'color' : 'black', 'dash' : 'dashdot'},
                   '97.5%'   : {'color' : 'black', 'dash' : 'dot'}}
dict_markers = {'2.5%'    : {'opacity' : 0, 'size' : 0},
                    '5%'   : {'opacity' : 0, 'size' : 0},
                    '10%'   : {'opacity' : 0, 'size' : 0},
                    '25%' : {'opacity' : 0, 'size' : 0},
                    '50%'   : {'opacity' : 0, 'size' : 0},
                    '75%'   : {'opacity' : 0, 'size' : 0},
                    '90%'   : {'opacity' : 0, 'size' : 0},
                    '95%'   : {'opacity' : 0, 'size' : 0},
                    '97.5%'   : {'opacity' : 0, 'size' : 0}}
fig = imfplotly.create_fig(forecasted_density_w_df_plot, linecols=linecols,
                               dict_colors=dict_colors,xfontsize=14,
                               dict_markers=dict_markers,
                               figtitle=ttl, xtitle='', ytitle=ylabel,
                               xangle=-90,margin_bottom =300,height=900,
                               margin_top=100,xnticks=len(forecasted_density_w_df_plot)+2)

    # Add fill between lines
fig = imfplotly.add_fill(forecasted_density_w_df_plot, '2.5%', '5%',
                             fig=fig,
                             colors='rgba(139,0,0,0.75)')

                             
fig = imfplotly.add_fill(forecasted_density_w_df_plot, '5%', '10%',
                             fig=fig,
                             colors='rgba(255,0,0,0.4)')

fig = imfplotly.add_fill(forecasted_density_w_df_plot, '10%', '25%',
                             fig=fig,
                             colors='rgba(0,0,255,0.15)')

fig = imfplotly.add_fill(forecasted_density_w_df_plot, '25%', '75%',
                             fig=fig,
                             colors='rgba(255,0,0,0.4)')
fig = imfplotly.add_fill(forecasted_density_w_df_plot, '75%', '90%',
                             fig=fig,
                             colors='rgba(0,0,255,0.15)')
fig = imfplotly.add_fill(forecasted_density_w_df_plot, '90%', '95%',
                             fig=fig,
                             colors='rgba(255,0,0,0.4)')
fig = imfplotly.add_fill(forecasted_density_w_df_plot, '95%', '97.5%',
                             fig=fig,
                             colors='rgba(139,0,0,0.75)')
    # Manage frequency of xticks & make sure the last one always visible
#    if xticks_freq:
#        start, end = ax.get_xlim()
#        t_seq = np.append(np.arange(start, end-5, xticks_freq), end)            
#        ax.xaxis.set_ticks(t_seq)
        



fig.update_xaxes(showgrid=False)
objects_cv.append(fig)



title = imfplotly.Heading1('Threshold for Combination Pool')
objects_cv.append(title)

text = (f'All models are ranked based on their cross-validated errors and then models are included in the pool as long as the'
        f'\n increase in error is gradual. To identify the relevant threshold, the following methodology is followed. Once the newly added model\'s.'
        f'\n  cross-validated error exceeds the threshold, this and its following models won\'t be included into the combination pool.')


markdown = imfplotly.Heading1(text,fontsize=14)
objects_cv.append(markdown)

fig = imfplotly.Image('intermediary results/threshold_eqn.png', text='',center=False)
objects_cv.append(fig)

title = imfplotly.Heading1('Weights for Model Combination', fontsize=14)
objects_cv.append(title)

text = 'The weight for model combining is calculated as:'
markdown = imfplotly.Heading3(text,fontsize=14)
objects_cv.append(markdown)


fig = imfplotly.Image('intermediary results/WeightedMean.png', text='',center=False)
objects_cv.append(fig)

text = 'Where x is the cross-validated error.'
markdown = imfplotly.Heading3(text,fontsize=14)
objects_cv.append(markdown)




imfplotly.create_html('html_report/cv.html', objects_cv,
                          links=backlink, # add link back to master file
                          show=False)

title = "Cross validation report"
 
 # Add to links
links[title] = "cv.html"








###############################################################################
###############################################################################

#--------------------------------------------------------------------
# Forecast report
#--------------------------------------------------------------------
###############################################################################
###############################################################################

objects_fcast = []


# Create HTML version of forecasting report
title = imfplotly.Heading1('Forecast Report')
objects_fcast.append(title)



title = imfplotly.Heading1('Combined Forecast', fontsize = 18)
objects_fcast.append(title)
text = (f'This section presents VaR forecast for {target_date} based on information of {forecast_based_on_date} by combing the models in the selection pools.')
markdown = imfplotly.Heading3(text,fontsize=14)
objects_fcast.append(markdown)
title = imfplotly.Heading1('Value at Risk Plot 1', fontsize = 16)
objects_fcast.append(title)
objects_fcast.append(fig_combined_density1)
text = f'Note: this plot shows combined mean and combined density separately'
markdown = imfplotly.Heading3(text,fontsize=14)
objects_fcast.append(markdown)
space = imfplotly.Space(2.5)
objects_fcast.append(space)

title = imfplotly.Heading1('Value at Risk Plot 2', fontsize = 16)
objects_fcast.append(title)
objects_fcast.append(fig_combined_density2)

text = f'Note: this plot shifted the combined distribution by combined mean'
markdown = imfplotly.Heading3(text,fontsize=14)
objects_fcast.append(markdown)

space = imfplotly.Space(2.5)
objects_fcast.append(space)

title = imfplotly.Heading1('Forecast using Best Density Model',fontsize = 18)
objects_fcast.append(title)

text = (f'This section presents VaR forecast for {target_dateb} based on information of {forecast_based_on_dateb} based on model {density_selected_table.index[0]}.'
        f'\n Also, it contains plots showing forecast dynamics from {dynamic_start} to the end of the series.')
markdown = imfplotly.Heading3(text,fontsize=14)
objects_fcast.append(markdown)
title = imfplotly.Heading1('Value at Risk Plot 3', fontsize = 16)
objects_fcast.append(title)
objects_fcast.append(fig_var_rule)

space = imfplotly.Space(2.5)
objects_fcast.append(space)

title = imfplotly.Heading1('PIT Test on the Model')
objects_fcast.append(title)
objects_fcast.append(fig_pit)





# Create HTML version of volatility plot
title = imfplotly.Heading1('Conditional FX Volatility Over Time', fontsize = 18)
objects_fcast.append(title)
objects_fcast.append(fig_conditional_vol_plot)

# Create HTML version of joy plot
text = (f'Joyplot Over Time from {dynamic_start}')
title = imfplotly.Heading1(text)
objects_fcast.append(title)
objects_fcast.append(fig_joyplot)
sampleflag = "in sample"
if jp_out_sample : sampleflag =  "out of sample"
text = (f'Note: This plot is generated {sampleflag}.')
markdown = imfplotly.Heading3(text,fontsize=14)
objects_fcast.append(markdown)

# Create HTML version of fan chart
text =(f'Fanchart Over Time from {dynamic_start}')
title = imfplotly.Heading1(text)
objects_fcast.append(title)
objects_fcast.append(fig_fanchart)
sampleflag = "in sample"
if fc_out_sample : sampleflag =  "out of sample"
text = (f'Note: This plot plot generated {sampleflag}.')
markdown = imfplotly.Heading3(text,fontsize=14)
objects_fcast.append(markdown)

# Create HTML version of conditional CDF
text = (f'Conditional CDF Over Time from {dynamic_start} with Exceedance(s)')
title = imfplotly.Heading1(text)
objects_fcast.append(title)
objects_fcast.append(fig_conditional_CDF)
sampleflag = "in sample"
if cd_out_sample : sampleflag =  "out of sample"
text = (f'Note: This plot is generated {sampleflag}.')
markdown = imfplotly.Heading3(text,fontsize=14)
objects_fcast.append(markdown)

text =(f'Conditional Exceedance(s) Over Time from {dynamic_start}')
title = imfplotly.Heading1(text)
objects_fcast.append(title)
objects_fcast.append(fig_Cond_exceedance)
objects_fcast.append(fig_Cond_exceedance2)
sampleflag = "in sample"
if cdv_out_sample : sampleflag =  "out of sample"
text = (f'Note: These two plots are generated {sampleflag}.')
markdown = imfplotly.Heading3(text,fontsize=14)
objects_fcast.append(markdown)

title = 'Forecast report'


imfplotly.create_html('html_report/fcast.html', objects_fcast,
                          links=backlink, # add link back to master file
                          show=False)
 # Add to links
links[title] = "fcast.html"


#import plotly.io as pio
#pio.renderers.default='browser'



#--------------------------------------------------------------------
# Create master file
#--------------------------------------------------------------------
imfplotly.create_html('html_report/master.html',
                      title='Report Main Page',
                      links=links)
