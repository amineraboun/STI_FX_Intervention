'''
2021-09-29 Kei Moriya

Create line + bar chart.
'''

import os
import sys
import importlib

import numpy as np
import pandas as pd

import plotly_utilities
importlib.reload(plotly_utilities)
from plotly_utilities import create_table, rgbstr_to_hexstr, create_html, \
     create_fig_lines_and_bars, create_fig_lines

WIDTH = 1500

# Add all figs to this list
figs = []

#--------------------------------------------------------------------
# Read in data
infilename = 'data/Nicaragua_remittances.csv'
if not os.path.isfile(infilename):
    print('File ' + infilename + ' does not exist')
    sys.exit(-1)
df = pd.read_csv(infilename, index_col=0, parse_dates=[0])

# Drop any periods that do not have any data
df.dropna(axis=0, how='all', inplace=True)
cols = df.columns

dict_colors={df.columns[0] : {'color' : 'black'}}

#--------------------------------------------------------------------
# Create lines + bar chart
figtitle = 'Nicaragua Remittances'
linecols = cols[0]
height = 400
fig = create_fig_lines_and_bars(df,
                                linecols=linecols,
                                figtitle=figtitle,
                                legend_title='',
                                dict_colors=dict_colors,
                                stack=False,
                                bar_right=True,
                                width=WIDTH,
                                xrange=30,
                                height=height)
figs.append(fig)

#--------------------------------------------------------------------
# Create table for GDP
fig2 = create_table(df, nperiods=30, width=WIDTH)
figs.append(fig2)

#--------------------------------------------------------------------
# Create output HTML file
outfilename = 'out_line_bar.html'
create_html(outfilename, figs,
            title='Nicaragua Remittances',
            datafilename=infilename)
