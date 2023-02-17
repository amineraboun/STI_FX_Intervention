'''
2021-09-22 Kei Moriya

Create HTML output using plotly.
Each fig object is exported as <div> tag which
can be embedded in output HTML file.
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
infilename = 'data/CostaRica_embi.csv'
if not os.path.isfile(infilename):
    print('File ' + infilename + ' does not exist')
    sys.exit(-1)
df = pd.read_csv(infilename, index_col=0, parse_dates=[0])

# Drop any periods that do not have any data
df.dropna(axis=0, how='all', inplace=True)

dict_colors = {df.columns[0] : {'color' : 'red'},
               df.columns[1] : {'color' : 'black'}}

#--------------------------------------------------------------------
# Create line chart for daily data
figtitle = 'Costa Rica EMBI (daily)'
linecols = df.columns[0]
height = 400
fig = create_fig_lines(df,
                       figtitle=figtitle,
                       dict_colors=dict_colors,
                       # linecols=linecols, # ['GDP', 'Imports'],
                       width=WIDTH,
                       xrange='2018:',
                       height=height)
figs.append(fig)

#--------------------------------------------------------------------
# Create table
fig2 = create_table(df, nperiods=30, num_format='.2f', width=WIDTH)
figs.append(fig2)

#--------------------------------------------------------------------
# Create output HTML file
outfilename = 'out_CostaRica.html'
create_html(outfilename, figs,
            title='Costa Rica EMBI',
            datafilename=infilename)
