'''
2021-09-12 Kei Moriya

Example of time series data table using go.Table.
'''

import os
import sys

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.colors import n_colors

def reformat_df(df, periods=False):
    '''
    Format df that is in datatools format so that
    - there is a column for "dates"
    - the col "dates" is formatted strings
    - the df is inverted so most recent dates appear at the top

    Returns the reformatted df.
    '''

    # Make a copy of original and work on it
    # so we don't influence the original.
    df = df.copy()

    # From the index, create a col "dates".
    # This is so that the col "dates" can be formatted as strings,
    # while keeping the original index for sorting and datetime operations.
    cols = list(df.columns)
    df['dates'] = df.index
    # Move "dates" col to beginning
    df = df[['dates'] + cols]

    # Format this col "dates" as str
    if not periods:
        df['dates'] = df['dates'].dt.strftime('%Y-%m')
    else:
        try:
            # Get frequency of data
            freq = df.index.to_period().freqstr
            if freq[0] == 'Q':
                df['dates'] = df['dates'].dt.to_period().dt.strftime('%yQ%q')
            elif freq[0] == 'M':
                df['dates'] = df['dates'].dt.to_period().dt.strftime('%Y-%m')
            elif freq[0] == 'A':
                df['dates'] = df['dates'].dt.to_period().dt.strftime('%Y')
            else:
                df['dates'] = df['dates'].dt.to_period().dt.strftime('%Y-%m-%d')
        except ValueError:
            print('WARNING: could not convert index to period,')
            print('using datetime formatting')
            df['dates'] = df['dates'].dt.strftime('%Y-%m-%d')
            
    # Sort on index so that latest dates are at top.
    df.sort_index(ascending=False, inplace=True)

    # Add bold to dates col.
    # (BAD IDEA, LEADS TO UNPREDICTABLE BEHAVIOR IN HTML)
    # if bold_dates:
    #     df['dates'] = '<b>' + df['dates'] + '</b>'

    return df    

def create_list_of_col_colors(cell_colors, length):
    '''
    Create a 2D list of colors that can be passed into
    go.Table to create alternating table rows.

    cell_colors should be a single color as str or
    a list of colors. If N colors are provided in this list,
    the table will alternate between these N colors.
    '''

    # If a str was passed in, convert to list.
    if type(cell_colors) == str:
        cell_colors = [cell_colors]
    elif type(cell_colors) != list:
        print('create_list_of_col_colors:')
        print('cell_colors should be list, given ' + str(type(cell_colors)) + ':')
        print(cell_colors)
        sys.exit(-1)

    # Get how many colors were passed in.
    ncolors = len(cell_colors)

    # Need to create list that alternates between these colors.
    col_colors = cell_colors * (length // ncolors) + cell_colors[:length % ncolors]
    return col_colors

def create_table(df,
                 num_format='.1f',
                 nperiods = 20, # set to None to show all
                 height='auto',
                 header_color='paleturquoise',
                 cell_colors=['lavender', 'white'],
                 periods=True,
                 date_width=150,
                 col_width=240,
                 header_height=45, # if too large, long text disappears?
                 row_height=20,
                 header_font_size=12,
                 cell_font_size=11,
                 header_align='left',
                 cell_align='center',
                 header_font_color='black',
                 cell_font_color='grey',
                 negative_color='red',
                 negative_threshold=0,
                 missing_font_color='blue'):
    '''
    Create table using DataFrame in datatools format,
    where index is DatetimeIndex with all columns
    representing one variable.
    '''

    global fig
    global df2

    # Cut off to most recent nperiods
    if type(nperiods) == int:
        df = df[-nperiods:]
    elif type(nperiods) is None:
        pass
    else:
        print('nperiods given as ' + str(type(nperiods)))
        print('Must be int or None')
        sys.exit(-1)
    
    # Format so that col "dates" is added and latest values are at top.
    df2 = reformat_df(df, periods=periods)

    # Create list of colors for columns
    col_colors = create_list_of_col_colors(cell_colors, len(df2))

    # Set font color and size for cells.
    # 0th col is "dates" so use header_font_color, header_font_size,
    # all other cols follow cell_font_color and cell_font_size.
    cell_font_colors = np.array([[header_font_color] * len(df2)] + [[cell_font_color] * len(df2)] * (len(df2.columns)-1))
    cell_font_sizes  = np.array([header_font_size] + [cell_font_size] * (len(df2.columns)-1))

    # Mask font colors based on values.
    # Use original df, not formatted df2, so we don't apply to col "dates" which is 0th col.
    # Make sure to reverse order of df so it matches df2.
    mask_neg = df.sort_index(ascending=False).copy()
    # Set values below negative_threshold to 1, otherwise 0.
    mask_neg = mask_neg.mask(mask_neg >= negative_threshold, np.nan)
    mask_neg = mask_neg.mask(mask_neg < negative_threshold, 1)
    mask_neg[pd.isnull(mask_neg)] = 0
    mask_neg = mask_neg.astype(bool)
    # Get values and transpose so it matches expected shape.
    mask_neg = mask_neg.values.T

    # Mask cell_font_colors using mask
    cell_font_colors[1:][mask_neg] = negative_color

    # Do the same for NA values
    mask_na = df.sort_index(ascending=False).copy()
    # Mask non-NA values as -999
    mask_na = mask_na.mask(~pd.isnull(mask_na), -999)
    # Mask NA values as 1
    mask_na = mask_na.mask(pd.isnull(mask_na), 1)
    # Mask non-NA values (-999) as 0
    mask_na = mask_na.mask(mask_na==-999, 0)
    mask_na = mask_na.astype(bool)
    mask_na = mask_na.values.T

    # Mask cell_font_colors using mask
    cell_font_colors[1:][mask_na] = missing_font_color

    # Plotly shows NA values as 0, so replace
    # any NA values with "---".
    # Together with "format", this will show as NaN.
    values = df2.replace(np.nan, '---').T.values

    assert(values.shape == cell_font_colors.shape)
    
    table = go.Table(header={'values'     : df2.columns,
                             'fill_color' : header_color,
                             'align'      : header_align,
                             'height'     : header_height,
                             'font'       : {'color' : header_font_color,
                                             'size'  : header_font_size}
                     },
                     cells={'values'     : values,
                            # 2-D list of colors for alternating rows.
                            # 0th col is for "dates", specify as header_color
                            'fill_color' : [header_color] + [col_colors] * (len(df2.columns)-1),
                            
                            'align'      : cell_align,
                            'height'     : row_height,
                            
                            'font'       : {'color' : cell_font_colors,
                                           # 'size'  : cell_font_sizes
                                           },
                            
                            # First col is "dates" so don't format as number
                            'format'     : [None] + [num_format] * (len(df2.columns)-1)
                     },
                     columnwidth=[date_width] +  [col_width] * (len(df2.columns)-1),
    )
    fig = go.Figure([table])

    # If the table needs scrolling, the font colors will wrap around
    # and start again, irrespective of the values.
    # To prevent this, set the height of the table to show all values.
    if height == 'auto':
        height = header_height + row_height * len(df) + 200
    fig.update_layout(height=height)
    return fig

def main(argv):
    # ------------------------------------------------------------------
    # Read in data for AUS GDP
    # ------------------------------------------------------------------
    global df
    infilename = 'data/Aus_GDP.csv'
    if not os.path.isfile(infilename):
        print('File ' + infilename + ' does not exist')
        sys.exit(-1)
    df = pd.read_csv(infilename, index_col=0, parse_dates=[0])

    # Drop any periods that do not have any data
    df.dropna(axis=0, how='all', inplace=True)

    ##########################################################
    # FOR DEBUGGING
    # Set latest GDP value to NA to test coloring
    df.loc[df.index[-1], 'GDP'] = np.nan
    ##########################################################
    
    fig = create_table(df)
    fig.show()

    # ------------------------------------------------------------------
    # Read in data for Dominican Republic inflation
    # ------------------------------------------------------------------
    global df2
    infilename = 'data/DominicanRepublic_inflation.csv'
    if not os.path.isfile(infilename):
        print('File ' + infilename + ' does not exist')
        sys.exit(-1)
    df2 = pd.read_csv(infilename, index_col=0, parse_dates=[0])

    # Drop any periods that do not have any data
    df2.dropna(axis=0, how='all', inplace=True)
    
    fig = create_table(df2)
    fig.show()
    
if __name__ == '__main__':
    main(sys.argv[1:])
