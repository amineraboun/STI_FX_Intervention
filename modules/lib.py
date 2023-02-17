from collections import OrderedDict

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.distributions.empirical_distribution import ECDF
import os
import sys
sys.path.append(os.path.abspath('modules'))
#import matplotlib.pyplot as plt
#import seaborn as sns
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
import imfplotly

from modules.distGARCH import closest

# This is the master file that links to each report.
masterfilename = 'master.html'
backlink = {'Back to index' : masterfilename}
links = OrderedDict()






# Plot the probability integral transform test.
# HTML output version of DistGARCHForecast::pit_plot(),
# see modules/distGARCH.py
def create_pit_plot(dgfor,
                    xlabel='Quantiles',
                    ylabel='Cumulative probability',
                    title=('Out-of-sample conditional density:'
                           ' Probability Integral Transform (PIT) test')):
        
    # Data work (note that the pit are computed by default)
    support = np.arange(0,1., 0.01)
    pits = dgfor.dfor['pit'].dropna().copy()

    # Compute the ecdf on the pits
    ecdf = ECDF(pits)

    # Fit it on the support
    pit_line = ecdf(support)

    # Compute the KS statistics (in case of need)
   # ks_stats = stats.kstest(dgfor.dfor['pit'].dropna(), 'uniform')

    # Confidence intervals based on Rossi and Shekopysan JoE 2019
    ci_u = [x+1.61*len(pits)**(-0.5) for x in support]
    ci_l = [x-1.61*len(pits)**(-0.5) for x in support]
    
    # Create df
    df = pd.DataFrame(index=support)
    df['Out-of-sample empirical CDF'] = pit_line
    df['Theoretical CDF'] = support
    df['1 percent critical values'] = ci_u
    df['ci_l'] = ci_l
    
    dict_colors = {'Out-of-sample empirical CDF' : {'color' : 'blue', 'width' : 2},
                   'Theoretical CDF' : {'color' : 'red', 'width' : 1},
                   '1 percent critical values' : {'color' : 'red', 'dash' : 'dash', 'width' : 1},
                   'ci_l' : {'color' : 'red', 'dash' : 'dash', 'width' : 1}
                   }
    
    dict_markers = {'Out-of-sample empirical CDF' : {'size' : 0, 'opacity' : 0},
                    'Theoretical CDF' : {'size' : 0, 'opacity' : 0},
                    '1 percent critical values' : {'size' : 0, 'opacity' : 0},
                    'ci_l' : {'size' : 0, 'opacity' : 0}
                    }

    fig = imfplotly.create_fig(df, linecols=['Out-of-sample empirical CDF', 'Theoretical CDF', '1 percent critical values'],
                               dict_colors=dict_colors,
                               dict_markers=dict_markers,
                               xtitle=xlabel, ytitle=ylabel,
                               hover_prec=3,
                               xrange=[-0.01,1.01]
                               )
    # Add line for cl_l without legend
    fig = imfplotly.add_lines(df, fig=fig, linecols='ci_l',
                              dict_colors=dict_colors,
                              dict_markers=dict_markers,
                              dict_legends={'ci_l' : False},
                              dict_hover={'ci_l' : 'skip'})

    return fig

def plot_pdf_rule(dgfor, fdate=None, q_low=0.05, q_high=0.95,ttle =None,
                  title=None, 
                  xlabel='', ylabel='density',
                  sample_lim=0.1):
    '''
    HTML version of distGARCHFit::plot_pdf_rule(),
    see modules/distGARCH.py.
    There is not ax option for this function compared to the original.
    '''

    # Take a sample at a given date
    sample = dgfor.sample.dropna()

    if fdate:
        assert fdate in sample.index, "Date not in data sample"
        ssample = sample.loc[fdate, :].values
    else: # Take the last date available
        ssample = sample.tail(1).values
        fdate = sample.tail(1).index[0].strftime('%Y-%m-%d')

    # Fit the distribution
    # I am lazy, the arch dist have no pdf readily done so I fit a sample..
    params_fit = dgfor.scipy_dist.fit(ssample)
    rv = dgfor.scipy_dist(*params_fit) # Frozen random variate
    # Create an evenly-spaced set of points that are
    # between sample_lim (%) and 100 - sample_lim (%) of ssample's range.
    # Note that these will not match exactly the values of ssample.
    _min = np.percentile(ssample, sample_lim)
    _max = np.percentile(ssample, 100-sample_lim)
    support = np.linspace(_min, _max, len(dgfor.sample.columns))

    # Compute the pdf for each point in support.
    pdf = rv.pdf(support)
    #pdf = self.scipy_dist.pdf(support)
        
    # Compute the quantiles to determine the intervention region
    qval_low = rv.ppf(q_low)
    qval_pdf_low = rv.pdf(qval_low)
    qval_high = rv.ppf(q_high)
    qval_pdf_high = rv.pdf(qval_high)
    
    # Compute the mode
    x_mode = support[list(pdf).index(max(pdf))]
    y_mode = rv.pdf(x_mode)

    # Create DataFrame
    df = pd.DataFrame(index=support)
    col = 'PDF'
    df[col] = pdf
    
    if title:
        ttl = title
    else:
        ttl = ttle
    
    # Create fig
    dict_colors = {col : {'width' : 3}}
    dict_markers = {col : {'opacity' : 0, 'size' : 0}}
    xrange = [min(support), max(support)]

    _vline = imfplotly.VLine(x=x_mode, line_dash='dash', opacity=1, line_color='blue')

    fig = imfplotly.create_fig(df, linecols=col,
                               dict_colors=dict_colors,
                               dict_markers=dict_markers,
                               dict_legends={col : False},
                               figtitle=ttl, xtitle=xlabel, ytitle=ylabel,
                               xrange=xrange,
                               hover_prec = 4,
                               vlines=[_vline],height=600,
                               margin_bottom=50, margin_left=120)
    
    # Fill Intervention regions
    # Add col for 0 values
    df['0'] = 0
    _df_lo = df[df.index <= qval_low].copy()
    _df_hi = df[qval_high < df.index].copy()
    # Rename col
    col = 'Intervention region'
    _df_lo.rename({'PDF' : col}, axis=1, inplace=True)
    _df_hi.rename({'PDF' : col}, axis=1, inplace=True)
    
    fig = imfplotly.add_fill(_df_lo, '0', col,
                             fig=fig,
                             dict_legends={col : True},
                             colors='rgba(255,0,0,1)')
    fig = imfplotly.add_fill(_df_hi, '0', col,
                             fig=fig,
                             colors='rgba(255,0,0,1)')

    # Add text and lines about VaR and Mode
    # Low quantile
    fig = imfplotly.add_text(f'VaR {100*q_low}%', qval_low, qval_pdf_low,
                             fig=fig,
                             color='darkred', xanchor='right', yanchor='bottom')
    fig = imfplotly.add_text('{:.1f}'.format(qval_low), 0.99*qval_low, 0,
                             fig=fig,
                             color='darkred', xanchor='left', yanchor='top')
    # Add line
    fig = imfplotly.add_segment(qval_low, 0, qval_low, qval_pdf_low,
                                fig,
                                color='black', width=3)

    
    # High quantile
    fig = imfplotly.add_text(f'VaR {100*q_high}%', qval_high, qval_pdf_high,
                             fig=fig,
                             color='darkred', xanchor='left', yanchor='bottom')
    fig = imfplotly.add_text('{:.1f}'.format(qval_high), 0.99*qval_high, 0,
                             fig=fig,
                             color='darkred', xanchor='right', yanchor='top')
    # Add line
    fig = imfplotly.add_segment(qval_high, 0, qval_high, qval_pdf_high,
                                fig,
                                color='black', width=3)

    # Mode
    fig = imfplotly.add_text(f'Mode', x_mode, y_mode,
                             fig=fig,
                             color='darkred', xanchor='center', yanchor='bottom')
    fig = imfplotly.add_text('{:.1f}'.format(x_mode), x_mode, 0,
                             fig=fig,
                             color='darkred', xanchor='left', yanchor='top')

    return fig



def plot_in_cond_vol(dgf,
                     start_date=None, 
                     title='In sample conditional volatility',
                     ylabel='Conditional volatility',
                     xticks_freq=None):
    '''
    HTML version of distGARCHFit::plot_in_cond_vol(),
    see modules/distGARCH.py.
    '''

    # Conditional volatility data
    cv = pd.DataFrame(dgf.res.conditional_volatility.dropna().copy())

    if start_date:
        cv = cv.loc[start_date:].copy()

    # Create fig
    dict_markers = {'cond_vol' : {'size' : 0.5}}
    fig = imfplotly.create_fig(cv, linecols='cond_vol',
                               dict_markers=dict_markers,
                               figtitle=title, xtitle='', ytitle=ylabel)
    return fig

def plot_conditional_cdf(dgfor,
                         q_low=0.05, q_high=0.95,
                         title=('Conditional cumulative distribution'
                                ' function and intervention thresholds'),
                         ylabel='quantile',
                         thresholds_t=None, 
                         swap_color=None,
                         size=100, 
                         xticks_freq=None):
    '''
    HTML version of distGARCHForecast::plot_conditional_cdf(),
    see modules/distGARCH.py.
    '''

    # Data work
    dcq = dgfor.dfor[dgfor.cond_quant_labels_l].dropna().copy()
    dcq.columns = [x.replace('cond_quant_', '') for x in dcq.columns]

    dates_l = dcq.index[:-1] # Don't take the last one

    dclose = pd.DataFrame(index=dates_l,
                          columns=['realization','cond_quant'])

    # Find the closest quantile in the list
    for fdate in dates_l:
        realization = dgfor.df.loc[fdate, dgfor.depvar]
        cond_quant_l = dcq.loc[fdate, :]
        closest_quantile_idx = closest(realization, cond_quant_l)[0]
        closest_quantile = cond_quant_l.index[closest_quantile_idx]
        dclose.loc[fdate, :] = [realization, closest_quantile]

    dclose['Quantile'] = 100*(dclose['cond_quant'].astype(float))

        
    if thresholds_t:
        # Add the fixed thresholds
        dv = dgfor.fixed_thresholds_FXI(thresholds_t)
        dclose = dclose.merge(dv[['FXI']],
                              left_index=True, right_index=True)

        da = dclose.loc[dclose['FXI']=='Above', :].copy()
        db = dclose.loc[dclose['FXI']=='Below', :].copy()
            
    else:
        dv = dgfor.VaR_FXI(qv_l=[q_low, q_high])
        dclose = dclose.merge(dv[['FXI']],
                              left_index=True, right_index=True)
        da = dclose.loc[dclose['FXI']=='Above', :].copy()
        db = dclose.loc[dclose['FXI']=='Below', :].copy()

    if swap_color:
        ctop = 'rgba(0,255,0,0.8)'  # green with alpha
        cdown = 'rgba(255,0,0,0.8)' # red with alpha
    else:
        ctop = 'rgba(255,0,0,0.8)'  # red with alpha
        cdown = 'rgba(0,255,0,0.8)' # green with alpha

    # Horizontal lines
    hlines = []
    _hline = imfplotly.HLine(y=100*q_low, line_color='red', line_dash='dash', line_width=2, text='')
    hlines.append(_hline)
    _hline = imfplotly.HLine(y=100*q_high, line_color='red', line_dash='dash', line_width=2, text='')
    hlines.append(_hline)
    _hline = imfplotly.HLine(y=25, line_color='blue', line_dash='solid', line_width=2, text='')
    hlines.append(_hline)
    _hline = imfplotly.HLine(y=50, line_color='black', line_dash='solid', line_width=2, text='')
    hlines.append(_hline)
    _hline = imfplotly.HLine(y=75, line_color='blue', line_dash='solid', line_width=2, text='')
    hlines.append(_hline)
        
    # Create fig
    dict_colors = {'Quantile' : {'width' : 3}}
    fig = imfplotly.create_fig(dclose, linecols='Quantile',
                               figtitle=title, xtitle='', ytitle=ylabel,
                               hlines=hlines)

    # Scatter lines with fixed thresholds
    dict_colors = {'Quantile' : {'color' : ctop,'width' : 0}}
    dict_markers = {'Quantile' : {'symbol' : 'diamond', 'size' : 15}}
    dict_legends = {'Quantile' : False}
    fig = imfplotly.add_lines(da, fig=fig,
                              linecols='Quantile',
                              dict_colors=dict_colors,
                              dict_markers=dict_markers,
                              dict_legends=dict_legends)

    dict_colors = {'Quantile' : {'color' : cdown,'width' : 0}}
    dict_markers = {'Quantile' : {'symbol' : 'circle', 'size' : 15}}
    dict_legends = {'Quantile' : False}
    fig = imfplotly.add_lines(db, fig=fig,
                              linecols='Quantile',
                              dict_colors=dict_colors,
                              dict_markers=dict_markers,
                              dict_legends=dict_legends)
    
#    # Add the ticks, if needed
#    new_t_l = [100*q_low, 25, 50, 75, 100*q_high]
#    #new_ticks_l = sorted(list(ax.get_yticks()) + new_t_l)
#    new_ticks_l = new_t_l
#    extra_idx_l = [new_ticks_l.index(x) for x in new_t_l]
#    ax.set_yticks(new_ticks_l) # Add new ticks
#
#    for idx in extra_idx_l: 
#        ax.get_yticklabels()[idx].set_color("darkred")            
#
#    # Manage frequency of xticks & make sure the last one always visible
#    if xticks_freq:
#        start, end = ax.get_xlim()
#        t_seq = np.append(np.arange(start, end-5, xticks_freq), end)
#        ax.xaxis.set_ticks(t_seq)

    return fig

def plot_fan_chart(dgfor,
                   title=None,
                   ylabel='',
                   xticks_freq=None):
    '''
    HTML version of distGARCHForecast::plot_fan_chart(),
    see modules/distGARCH.py.
    '''

    # Select the quantiles
    qfc_l = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
    qfc_labels_l = [f'cond_quant_{x}' for x in qfc_l]

    dfc = dgfor.dfor[['true_val'] + qfc_labels_l].copy()
    #dfc = dgfor_dynamic.dfor[['true_val'] + qfc_labels_l].copy()

    dfc.columns = [x.replace('cond_quant_', '') for x in dfc.columns]

    # Rename cols
    dfc.rename({'0.05' : '5th', '0.1' : '10th',
                '0.25' : '25th', '0.5' : 'Median',
                '0.75' : '75th', '0.9' : '90th',
                '0.95' : '95th'}, axis=1, inplace=True)

    if title is None:
        t1 = f'Fan chart of predictive {dgfor.depvar}'
        ttl = t1 + '\n 1, 5, 10, 25, 50, 75, 90, 95 Conditional Quantiles'
    else:
        ttl=title

    # Create fig
    linecols = ['5th', '10th', '25th',
                'Median', '75th', '90th', '95th']
    dict_colors = {'5th'    : {'color' : 'black', 'dash' : 'dot'},
                   '10th'   : {'color' : 'black', 'dash' : 'dashdot'},
                   '25th'   : {'color' : 'black', 'dash' : 'dash'},
                   'Median' : {'color' : 'black', 'width' : 2},
                   '75th'   : {'color' : 'black', 'dash' : 'dash'},
                   '90th'   : {'color' : 'black', 'dash' : 'dashdot'},
                   '95th'   : {'color' : 'black', 'dash' : 'dot'}}
    dict_markers = {'5th'    : {'opacity' : 0, 'size' : 0},
                    '10th'   : {'opacity' : 0, 'size' : 0},
                    '25th'   : {'opacity' : 0, 'size' : 0},
                    'Median' : {'opacity' : 0, 'size' : 0},
                    '75th'   : {'opacity' : 0, 'size' : 0},
                    '90th'   : {'opacity' : 0, 'size' : 0},
                    '95th'   : {'opacity' : 0, 'size' : 0}}
    fig = imfplotly.create_fig(dfc, linecols=linecols,
                               dict_colors=dict_colors,
                               dict_markers=dict_markers,
                               figtitle=ttl, xtitle='', ytitle=ylabel,
                               xangle=-45,
                               margin_top=100)

    # Add fill between lines
    fig = imfplotly.add_fill(dfc, '5th', '10th',
                             fig=fig,
                             colors='rgba(139,0,0,0.75)')
    fig = imfplotly.add_fill(dfc, '90th', '95th',
                             fig=fig,
                             colors='rgba(139,0,0,0.75)')
                             
    fig = imfplotly.add_fill(dfc, '10th', '25th',
                             fig=fig,
                             colors='rgba(255,0,0,0.4)')
    fig = imfplotly.add_fill(dfc, '75th', '90th',
                             fig=fig,
                             colors='rgba(255,0,0,0.4)')

    fig = imfplotly.add_fill(dfc, '25th', '75th',
                             fig=fig,
                             colors='rgba(0,0,255,0.15)')

    # Manage frequency of xticks & make sure the last one always visible
#    if xticks_freq:
#        start, end = ax.get_xlim()
#        t_seq = np.append(np.arange(start, end-5, xticks_freq), end)            
#        ax.xaxis.set_ticks(t_seq)
        
    return fig



   # VaR exceedance
def plot_var_exceedance(dgfor_dynamic, qv_l=[0.025, 0.975],lineval = 'true_val',
                        swap_color=None,title = '',margin_bottom = 100,
                        y1='Below',margin_top = 100, y2='Above',size=100):
        
    """ 
        Plot the VaR Exceedance 
        On the dependent variable, also possible to indicate level

        qv_l: list of two quantiles, 
              List of the upper and below quantiles
 

    """
    qv_l = sorted(qv_l)
    v_labels_l = [f'cond_quant_{x:g}' for x in qv_l]
        
    
    
    
    
    # Prepare the frame
    dv = dgfor_dynamic.VaR_FXI(qv_l)
        
    # Subselect the frame and plot it
    dvs = dv.loc[dgfor_dynamic.start_date:, :].copy()
    dvs[f'at {qv_l[0]*2*100} Percent'] = dvs[lineval]
    dvs[f'below VaR {qv_l[0]*100} percent'] = dvs[y1]
    dvs[f'above VaR {qv_l[1]*100}  percent)'] = dvs[y2]    
    
    if swap_color:
            ctop = 'rgba(0,255,0,0.8)'  # green with alpha
            cdown = 'rgba(255,0,0,0.8)' # red with alpha
    else:
            ctop = 'rgba(255,0,0,0.8)'  # red with alpha
            cdown = 'rgba(0,255,0,0.8)' # green with alpha
     
        
     

        
        # First plot
        #f'at {qv_l[0]*2*100} Percent'

    fig = imfplotly.create_fig(dvs, linecols=f'at {qv_l[0]*2*100} Percent',margin_top=100,margin_bottom = 10,height = 400,
                          figtitle=title, xtitle='', ytitle='',dict_legends= {f'at {qv_l[0]*2*100} Percent' :True})

        # Scatter lines with fixed thresholds
    dict_colors = {f'below VaR {qv_l[0]*100} percent' : {'color' : cdown,'width' : 0}}
    dict_markers = {f'below VaR {qv_l[0]*100} percent' : {'symbol' : 'diamond', 'size' : 15}}
    dict_legends = {f'below VaR {qv_l[0]*100} percent' : True}
    fig = imfplotly.add_lines(dvs, fig=fig,
                          linecols=f'below VaR {qv_l[0]*100} percent',
                          dict_colors=dict_colors,
                          dict_markers=dict_markers,
                          dict_legends=dict_legends)
 #'above VaR {qv_l[1]*100}  percent)'    
    dict_colors = {f'above VaR {qv_l[1]*100}  percent)' : {'color' : ctop,'width' : 0}}
    dict_markers = {f'above VaR {qv_l[1]*100}  percent)' : {'symbol' : 'circle', 'size' : 15}}
    dict_legends = {f'above VaR {qv_l[1]*100}  percent)' : True}
    fig = imfplotly.add_lines(dvs, fig=fig,
                          linecols= f'above VaR {qv_l[1]*100}  percent)',
                          dict_colors=dict_colors,
                          dict_markers=dict_markers,
                          dict_legends=dict_legends)

    
        
        
    return fig

def plot_combined_density(df,forecasted_mean_val,lower_bound,upper_bound,fdate=None, q_low=0.025, q_high=0.975,ttle =None,
                  title=None,
                  xlabel='', ylabel='',
                  sample_lim=0.1):
    '''
    Notes here
 
    '''
   
    col1 = 'Combined_density'


    # Create fig
    dict_colors = {col1 : {'width' : 3}}
    dict_markers = {col1 : {'opacity' : 0, 'size' : 0}}
    #xrange = [min(support), max(support)]

    _vline = imfplotly.VLine(x=forecasted_mean_val, line_dash='dash', opacity=1, line_color='green',text=' Combined Mean')

    fig = imfplotly.create_fig(df, linecols=col1,
                               dict_colors=dict_colors,
                               dict_markers=dict_markers,
                               dict_legends={col1 : False},
                               figtitle=title, xtitle=xlabel, ytitle=ylabel,
                             #  xrange=xrange,
                               hover_prec = 4,
                               vlines=[_vline],height =700,
                               margin_top=100, margin_left=120)
    
    # Fill Intervention regions
    # Add col for 0 values
    df['0'] = 0
    _df_lo = df[df.index <= lower_bound].copy()
    _df_hi = df[upper_bound < df.index].copy()
    # Rename col
    col1 = 'Intervention region'
    _df_lo.rename({'Combined_density' : col1}, axis=1, inplace=True)
    _df_hi.rename({'Combined_density' : col1}, axis=1, inplace=True)
    
    fig = imfplotly.add_fill(_df_lo, '0', col1,
                             fig=fig,
                             dict_legends={col1 : True},
                             colors='rgba(255,0,0,1)')
    fig = imfplotly.add_fill(_df_hi, '0', col1,
                             fig=fig,
                             colors='rgba(255,0,0,1)')

    # Add text and lines about VaR and Mode
    # Low quantile
    fig = imfplotly.add_text(f'VaR {100*q_low}%',lower_bound ,0.00025 ,
                             fig=fig,
                             color='darkred', xanchor='right', yanchor='bottom')
    fig = imfplotly.add_text('{:.1f}'.format(lower_bound), 0.99*lower_bound, 0,
                             fig=fig,
                             color='darkred', xanchor='left', yanchor='top')
    # Add line
    #fig = imfplotly.add_segment(q_low, 0, q_low, lower_bound,
    #                            fig,
    #                            color='black', width=3)

    
    # High quantile
    fig = imfplotly.add_text(f'VaR {100*q_high}%',upper_bound,0.00025,fig=fig,
                             color='darkred', xanchor='left', yanchor='bottom')
    fig = imfplotly.add_text('{:.1f}'.format(upper_bound), 0.99*upper_bound, 0,
                             fig=fig,
                             color='darkred', xanchor='right', yanchor='top')
    # Add line
   # fig = imfplotly.add_segment(q_high, 0, q_high, upper_bound,
   ##                             fig,
    #                            color='black', width=3)

    # Mode
    fig = imfplotly.add_text('', forecasted_mean_val, 0,
                             fig=fig,
                             color='darkred', xanchor='center', yanchor='bottom')
    fig = imfplotly.add_text('{:.1f}'.format(forecasted_mean_val), forecasted_mean_val, 0,
                             fig=fig,
                            color='darkred', xanchor='left', yanchor='top')

    return fig



def plot_fan_chart_cond_mean(dfc,
                   title=None,figtitle=None,
                   ylabel='',
                   xticks_freq=None):
    '''
    HTML version of distGARCHForecast::plot_fan_chart(),
    see modules/distGARCH.py.
    '''

   

    if title is None:
        t1 = f'Fan chart of predictive {figtitle}'
        ttl = t1 + '\n 5, 10, 25, 50, 75, 90, 95 Conditional Quantiles'
    else:
        ttl=title

    # Create fig
    linecols = ['5th', '10th', '25th',
                'Median', '75th', '90th', '95th']
    dict_colors = {'5th'    : {'color' : 'black', 'dash' : 'dot'},
                   '10th'   : {'color' : 'black', 'dash' : 'dashdot'},
                   '25th'   : {'color' : 'black', 'dash' : 'dash'},
                   'Median' : {'color' : 'black', 'width' : 2},
                   '75th'   : {'color' : 'black', 'dash' : 'dash'},
                   '90th'   : {'color' : 'black', 'dash' : 'dashdot'},
                   '95th'   : {'color' : 'black', 'dash' : 'dot'}}
    dict_markers = {'5th'    : {'opacity' : 0, 'size' : 0},
                    '10th'   : {'opacity' : 0, 'size' : 0},
                    '25th'   : {'opacity' : 0, 'size' : 0},
                    'Median' : {'opacity' : 0, 'size' : 0},
                    '75th'   : {'opacity' : 0, 'size' : 0},
                    '90th'   : {'opacity' : 0, 'size' : 0},
                    '95th'   : {'opacity' : 0, 'size' : 0}}
    fig = imfplotly.create_fig(dfc, linecols=linecols,
                               dict_colors=dict_colors,
                               dict_markers=dict_markers,
                               figtitle=ttl, xtitle='', ytitle=ylabel,
                               xangle=-45,
                               margin_top=100)

    # Add fill between lines
    fig = imfplotly.add_fill(dfc, '5th', '10th',
                             fig=fig,
                             colors='rgba(139,0,0,0.75)')
    fig = imfplotly.add_fill(dfc, '90th', '95th',
                             fig=fig,
                             colors='rgba(139,0,0,0.75)')
                             
    fig = imfplotly.add_fill(dfc, '10th', '25th',
                             fig=fig,
                             colors='rgba(255,0,0,0.4)')
    fig = imfplotly.add_fill(dfc, '75th', '90th',
                             fig=fig,
                             colors='rgba(255,0,0,0.4)')

    fig = imfplotly.add_fill(dfc, '25th', '75th',
                             fig=fig,
                             colors='rgba(0,0,255,0.15)')

    # Manage frequency of xticks & make sure the last one always visible
#    if xticks_freq:
#        start, end = ax.get_xlim()
#        t_seq = np.append(np.arange(start, end-5, xticks_freq), end)            
#        ax.xaxis.set_ticks(t_seq)
        
    return fig







def generate_forecast_report(outfilename, objects):
    '''
    Generate report based on returns data.
    '''

    imfplotly.create_html(outfilename, objects,
                          links=backlink, # add link back to master file
                          show=False)
    title = 'GARCH Analysis'
    # Add to links
    links[title] = outfilename
    
def generate_master_report():
    imfplotly.create_html(masterfilename,
                          title='Summary Report for Mauritius',
                          links=links)
    
