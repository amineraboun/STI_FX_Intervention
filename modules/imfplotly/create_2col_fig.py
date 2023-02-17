'''
2021-09-25 Kei Moriya

Create HTML output for double col figures using plotly.
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
infilename = 'data/Aus_labor.csv'
if not os.path.isfile(infilename):
    print('File ' + infilename + ' does not exist')
    sys.exit(-1)
df = pd.read_csv(infilename, index_col=0, parse_dates=[0])

# Drop any periods that do not have any data
df.dropna(axis=0, how='all', inplace=True)

dict_colors = {df.columns[0] : {'color' : 'red'}}

#--------------------------------------------------------------------
# Create 2-col line chart
figtitle = ['Unemployment Rate', 'Australia Labor Market']
# linecolslist should be list of 2 or 4 elements.
# If 2 elements, they are for the left and right column charts.
# If 4 elements, they are for the left and right y-axes for the left and right charts.
# If nothing is to be plotted on a given y-axis, provide None.
linecolslist = [df.columns[0], None, df.columns[1], df.columns[2]]
height = 400

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
_hrect2 = HRect(y0=40, y1=50, rect_color='blue', col=2, fill_color='green')
hrects = [_hrect, _hrect2]

# vrects
_vrect = VRect(x0='2020-01', x1='2020-07', text='2020 1st half', col=1)
_vrect2 = VRect(x0='2021-01', x1='2021-07', text='2021 1st half', fill_color='blue', text_color='blue', opacity=0.2, col=2)
vrects = [_vrect, _vrect2]

fig = create_fig_2col_lines(df,
                            dict_colors=dict_colors,
                            linecolslist=linecolslist,
                            figtitle=figtitle,
                            legend_title='',
                            width=WIDTH,
                            xrange=30,
                            hlines=hlines,
                            vlines=vlines,
                            hrects=hrects,
                            vrects=vrects,
                            height=height)
figs.append(fig)

#--------------------------------------------------------------------
# Create table for labor market
fig2 = create_table(df, nperiods=30, width=WIDTH)
figs.append(fig2)

#--------------------------------------------------------------------
# Create output HTML file
outfilename = 'out_labor.html'
create_html(outfilename, figs,
            title='Australia Labor Market',
            datafilename=infilename)
