'''
Example of Bokeh table using bokeh_utilities.py.
'''

import os
import sys

import numpy as np
import pandas as pd

from imf_datatools import get_haver_data
from imf_datatools.dataframe_utilities import calc_yoy

import bokeh_utilities
scripts = []
divs = []

# -------------------------------------------------------------------------------
# US GDP
# -------------------------------------------------------------------------------
dict_cols = {'PGDPH@USECON' : 'GDP',
             'PTCH@USECON' : 'C',
             'PTGH@USECON' : 'G',
             'PTFH@USECON' : 'I',
             'PTVH@USECON' : 'Inventories',
             'PTXH@USECON' : 'X',
             'PTMH@USECON' : 'M'}
df = get_haver_data(list(dict_cols.keys()))
df.columns = df.columns.map(dict_cols)

# Generate Bokeh script, div
script, div = bokeh_utilities.create_bokeh_table(df,
                                                 decimals=2,
                                                 nperiods=15,
                                                 dateformat='%Y-%m-%d') # %b%y
# Append to list of scripts, divs
scripts.append(script)
divs.append(div)

# -------------------------------------------------------------------------------
# Nicaragua Remittances
# -------------------------------------------------------------------------------
_df1 = calc_yoy(get_haver_data('N278BW@EMERGELA'))
_df1.columns = ['yoy growth']
_df2 = get_haver_data('N278BW@EMERGELA')
_df2.columns = ['Level']
df2 = _df1.merge(_df2, left_index=True, right_index=True, how='outer')

# Generate Bokeh script, div
script, div = bokeh_utilities.create_bokeh_table(df2,
                                                 decimals=2,
                                                 nperiods=25,
                                                 dateformat='%Y-%m') # %b%y
# Append to list of scripts, divs
scripts.append(script)
divs.append(div)

# Generate output HTML
outfilename = 'output.html'
bokeh_utilities.generate_html(outfilename, scripts, divs)
