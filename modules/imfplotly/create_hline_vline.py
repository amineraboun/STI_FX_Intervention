'''
2021-09-27 Kei Moriya

Create HTML output using plotly.
Each fig object is exported as <div> tag which
can be embedded in output HTML file.

Create file with dual y-axis line chart with hlines and vlines.
'''

import os
import sys
import importlib

import numpy as np
import pandas as pd

import plotly_utilities
importlib.reload(plotly_utilities)
from plotly_utilities import create_table, rgbstr_to_hexstr, create_html, \
     create_fig_lines_and_bars, create_fig_lines, create_fig_2col_lines, \
     HLine, VLine, HRect, VRect


WIDTH = 1500

# Add all figs to this list
figs = []

#--------------------------------------------------------------------
# Read in data
infilename = 'data/Mexico_inflation.csv'
if not os.path.isfile(infilename):
    print('File ' + infilename + ' does not exist')
    sys.exit(-1)
df = pd.read_csv(infilename, index_col=0, parse_dates=[0])

# Drop any periods that do not have any data
df.dropna(axis=0, how='all', inplace=True)

dict_colors = {df.columns[0] : {'color' : 'red'},
               df.columns[1] : {'color' : 'blue'},
               df.columns[2] : {'color' : 'green'}}

#--------------------------------------------------------------------
# Create 2-col lines
linecolslist = [list(df.columns[0:2]), None, df.columns[2], df.columns[3]]
figtitle = ['Mexico CPI', 'CPI Forecasts']
height = 600
_hline = HLine(y=3, text='Inflation target')
_vline = VLine(x='2020-06', text='start period', col=1)
_hrect = HRect(y0=2.5, y1=4.5, text='Inflation target range', col=1)
_vrect = VRect(x0='2020-07', x1='2021-01', text='Focus period', col=2)
fig = create_fig_2col_lines(df,
                            linecolslist=linecolslist,
                            figtitle=figtitle,
                            legend_title='Seasonally Adjusted',
                            dict_colors=dict_colors,
                            width=WIDTH,
                            xrange=25,
                            yrange=[0,10],
                            height=height,
                            hlines=[_hline],
                            vlines=[_vline],
                            hrects=[_hrect],
                            vrects=[_vrect])

figs.append(fig)

#--------------------------------------------------------------------
# Create table for GDP
fig2 = create_table(df, nperiods=20, width=WIDTH)
figs.append(fig2)

#--------------------------------------------------------------------
# Create output HTML file
outfilename = 'out_hline_vline.html'
create_html(outfilename, figs,
            title='Mexico Inflation',
            datafilename=infilename)
