'''
2021-09-16 Kei Moriya

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

import plotly_utilities
importlib.reload(plotly_utilities)
from plotly_utilities import create_table, rgbstr_to_hexstr, create_html, \
     create_fig_lines_and_bars, create_fig_lines, \
     HLine, VLine, HRect, VRect

WIDTH = 1500

# Add all figs to this list
figs = []

#--------------------------------------------------------------------
# Read in data
infilename = 'data/Aus_GDP.csv'
if not os.path.isfile(infilename):
    print('File ' + infilename + ' does not exist')
    sys.exit(-1)
df = pd.read_csv(infilename, index_col=0, parse_dates=[0])

# Drop any periods that do not have any data
df.dropna(axis=0, how='all', inplace=True)
gdpcols = df.columns

#--------------------------------------------------------------------
# Create lines + stacked bars for GDP
figtitle = 'Australia GDP by Components'
linecols = gdpcols[0]
height = 400
dict_colors = {gdpcols[0] : {'color' : 'blue',
                             'width' : 4,
                             'dash'  : None}
               }

# hlines
_hline = HLine(y=10)
_hline2 = HLine(y=15, line_color='blue')
hlines = [_hline, _hline2]

# vlines
_vline = VLine(x='2020-01', text='Start of 2020')
_vline2 = VLine(x='2021-01', text='Start of 2021', line_color='blue', text_color='blue')
vlines = [_vline, _vline2]

# hrects
_hrect = HRect(y0=10, y1=12, col=1, fill_color='cyan')
_hrect2 = HRect(y0=40, y1=50, rect_color='blue', fill_color='green')
hrects = [_hrect, _hrect2]

# vrects
_vrect = VRect(x0='2020-01', x1='2020-07', text='2020 1st half')
_vrect2 = VRect(x0='2021-01', x1='2021-07', text='2021 1st half', fill_color='blue', text_color='blue', opacity=0.2)
vrects = [_vrect, _vrect2]

fig = create_fig_lines_and_bars(df,
                                linecols=linecols,
                                dict_colors=dict_colors,
                                figtitle=figtitle,
                                legend_title='',
                                bar_opacity=0.7,
                                xrange=30,
                                hlines=hlines,
                                vlines=vlines,
                                hrects=hrects,
                                vrects=vrects,
)
figs.append(fig)

#--------------------------------------------------------------------
# Create table for GDP
fig2 = create_table(df, nperiods=30, width=WIDTH)
figs.append(fig2)

#--------------------------------------------------------------------
# Create output HTML file
outfilename = 'out_gdp.html'
create_html(outfilename, figs,
            title='Australia GDP',
            datafilename=infilename)
