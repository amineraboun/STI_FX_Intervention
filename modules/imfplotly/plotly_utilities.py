'''
2021/08/29 Kei Moriya

Library to easily customize Plotly output.

Functions that take in **kwargs will pop each valid keyword
and replace with default if not given.
This way all remaining invalid keywords can be shown to user as warning.
'''

import os
import sys
import inspect

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Initialize global stackgroup variable.
# This provides a unique stackgroup name to each set of stacked areas,
# so that multiple stacked areas could be plotted if needed.
STACKGROUP = 0

def update_legend(fig, **kwargs):
    legend_title           = kwargs.pop('legend_title', '')
    legend_bgcolor         = kwargs.pop('legend_bgcolor', None)
    legend_borderwidth     = kwargs.pop('legend_borderwidth', 1)
    legend_bordercolor     = kwargs.pop('legend_bordercolor', 'white')
    legend_title_font_size = kwargs.pop('legend_title_font_size', 14)
    legend_font_size       = kwargs.pop('legend_font_size', 10)

    if len(kwargs) > 0:
        # Get this function's name using the inspect module
        fname = inspect.stack()[0][3]
        print('WARNING:')
        print('In plotly_utilities::' + fname + ', the following keys were not used:')
        print(' - ', end='')
        print('\n - '.join([str(key) for key in kwargs]))
    
    fig.update_layout(legend_title_text=legend_title,
                      legend_bgcolor=legend_bgcolor,
                      legend_borderwidth=legend_borderwidth,
                      legend_bordercolor=legend_bordercolor,
                      legend_font_size=legend_font_size,
                      legend_title_font_size=legend_title_font_size)
    
def reformat_df_for_table(df, indextype='date', periods=False):
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
    if indextype == 'date':
        idxname = 'dates'
    else:
        idxname = df.index.name
        if idxname is None:
            idxname = 'index'
    df[idxname] = df.index
    # Move index col to beginning
    df = df[[idxname] + cols]

    # Format this col "dates" as str
    if indextype == 'date':
        if not periods:
            df['dates'] = df['dates'].dt.strftime('%Y-%m-%d')
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
                 indextype='date',
                 num_format='.1f',
                 nperiods = 20, # set to None to show all
                 as_cols=True,
                 height='auto',
                 width='auto',
                 header_color='paleturquoise',
                 cell_colors=['lavender', 'white'],
                 periods=True,
                 index_width='auto',
                 col_width='auto',
                 header_height=45, # if too large, long text disappears?
                 row_height=25,
                 header_font_size=16,
                 cell_font_size=11,
                 header_align='left',
                 cell_align='center',
                 header_font_color='black',
                 cell_font_color='grey',
                 mask=True,
                 negative_color='red',
                 negative_threshold=0,
                 missing_font_color='blue'):
    '''
    Create table using DataFrame in datatools format,
    where index is DatetimeIndex with all columns
    representing one variable.
    '''

    global fig
    global _df
    global df2
    global cell_font_colors
    global cell_font_sizes
    global values
    global mask_neg
    global mask_na

    # Cut off to most recent nperiods
    if type(nperiods) == int:
        df = df[-nperiods:]
    elif nperiods is None:
        pass
    else:
        print('nperiods given as ' + str(type(nperiods)))
        print('Must be int or None')
        sys.exit(-1)

    # Save df as global var
    _df = df
    
    # Format so that col "dates" is added and latest values are at top.
    df2 = reformat_df_for_table(df, indextype=indextype, periods=periods)

    # Show each column of df as a column.
    if as_cols:
        # Create list of colors for columns
        col_colors = create_list_of_col_colors(cell_colors, len(df2))

        # Set font color and size for cells.
        # 0th col is "dates" so use header_font_color, header_font_size,
        # all other cols follow cell_font_color and cell_font_size.
        cell_font_colors = np.array([[header_font_color] * len(df2)] + [[cell_font_color] * len(df2)] * (len(df2.columns)-1))
        cell_font_sizes  = np.array([header_font_size] + [cell_font_size] * (len(df2.columns)-1))
        
        if mask:
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
        
        headers = df2.columns

        format_vals = []
        # For each column, append [None] if date type,
        # and [num_format] for numeric type.
        datecols = df2.select_dtypes(include=[np.datetime64]).columns
        numcols =  df2.select_dtypes(include=[np.number]).columns
        for col in df2.columns:
            if col in datecols:
                format_vals += [None]
            elif col in numcols:
                format_vals += [num_format]
            elif df2[col].dtype.name == 'object':
                format_vals += [num_format]
            else:
                print('WARNING: unknown col type ' + str(df2[col].dtype))
                format_vals += [None]
        
        if index_width == 'auto':
            index_width = 200
        if col_width == 'auto':
            col_width = 150
        
    # Show each column of df as a row.
    else:
        # Create list of colors for columns
        col_colors = create_list_of_col_colors(cell_colors, len(df2.columns))

        # Set font color and size for cells.
        # 0th col is "dates" so use header_font_color, header_font_size,
        # all other cols follow cell_font_color and cell_font_size.
        cell_font_colors = np.array([[header_font_color] * len(df2.columns)] + [[cell_font_color] * len(df2.columns)] * (len(df2)-1))
        cell_font_sizes  = np.array([header_font_size] + [cell_font_size] * (len(df2)-1))
        
#        # Mask font colors based on values.
#        # Use original df, not formatted df2, so we don't apply to col "dates" which is 0th col.
#        # Make sure to reverse order of df so it matches df2.
#        mask_neg = df.sort_index(ascending=False).copy()
#        # Set values below negative_threshold to 1, otherwise 0.
#        mask_neg = mask_neg.mask(mask_neg >= negative_threshold, np.nan)
#        mask_neg = mask_neg.mask(mask_neg < negative_threshold, 1)
#        mask_neg[pd.isnull(mask_neg)] = 0
#        mask_neg = mask_neg.astype(bool)
#        # Get values and transpose so it matches expected shape.
#        mask_neg = mask_neg.values.T
#        
#        # Mask cell_font_colors using mask
#        cell_font_colors[1:][mask_neg] = negative_color
#        
#        # Do the same for NA values
#        mask_na = df.sort_index(ascending=False).copy()
#        # Mask non-NA values as -999
#        mask_na = mask_na.mask(~pd.isnull(mask_na), -999)
#        # Mask NA values as 1
#        mask_na = mask_na.mask(pd.isnull(mask_na), 1)
#        # Mask non-NA values (-999) as 0
#        mask_na = mask_na.mask(mask_na==-999, 0)
#        mask_na = mask_na.astype(bool)
#        mask_na = mask_na.values.T
#        
#        # Mask cell_font_colors using mask
#        cell_font_colors[1:][mask_na] = missing_font_color
        
        # Plotly shows NA values as 0, so replace
        # any NA values with "---".
        # Together with "format", this will show as NaN.
        values = []
        # Add columns as first element
        values.append(list(df.columns))
        # Add values as next elements.
        # Need to flip
        values += df.replace(np.nan, '---').values.tolist()
        
        headers = [''] + [t.strftime('%Y-%m') for t in df.index]

        # First col is column names so don't format as number
        format_vals = []
        # For each column, append [None] if date type,
        # and [num_format] for numeric type.
        datecols = df2.select_dtypes(include=[np.datetime64]).columns
        numcols =  df2.select_dtypes(include=[np.number]).columns
        for col in df2.columns:
            if col in datecols:
                format_vals += [None]
            elif col in numcols:
                format_vals += [num_format]
            elif df2[col].dtype.name == 'object':
                format_vals += [num_format]
            else:
                print('WARNING: unknown col type ' + str(df2[col].dtype))
                format_vals += [None]

        if index_width == 'auto':
            index_width = 500
        if col_width == 'auto':
            col_width = 120
        
    # end of as_cols is False
        
    # assert(values.shape == cell_font_colors.shape)
    
    table = go.Table(header={'values'     : headers,
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
                            'format'     : format_vals
                     },
                     columnwidth=[index_width] +  [col_width] * (len(df2.columns)-1),
    )
    fig = go.Figure([table])

    # If the table needs scrolling, the font colors will wrap around
    # and start again, irrespective of the values.
    # To prevent this, set the height of the table to show all values.
    if height == 'auto':
        if as_cols:
            height = header_height + row_height * len(df) + 300
        else:
            height = header_height + row_height * len(df.columns) + 300

    # If width is default of "auto", calculate necessary width
    # based on number of columns.
    if width == 'auto':
        if as_cols:
            width = index_width + col_width * (len(df2.columns)-1)
        else:
            width = index_width + col_width * len(df)
    fig.update_layout(height=height, width=width)

    return fig

def hexstr_to_rgbstr(hexstr):
    '''
    Convert hex str like #cdff9c to
    rgb str like rgb(205, 156, 255).
    '''

    # Convert hex str to int in base 16
    hexint = int(hexstr.replace('#', ''), 16)

    # Get the RGB values
    r, g, b = Blue =  (hexint >> 16) & 255, (hexint >> 8) & 255, hexint & 255
    r, g, b = str(r), str(g), str(b)

    # Format into final rgb str
    rgbstr = 'rgb(' + ', '.join((r,g,b)) + ')'

    return rgbstr

def rgbstr_to_hexstr(rgbstr):
    '''
    Convert rgb str like rgb(205, 156, 255) to
    hex str like #cdff9c.
    '''

    # Convert rgb str to int vals
    rgbvals = [v.strip() for v in rgbstr.replace('rgb(', '').replace(')','').split(',')]
    if len(rgbvals) != 3:
        print('Could not convert ' + str(rgbstr) + ' to triplet of RGB')
        sys.exit(-1)
    # Convert each of r, g, b to hex values
    hexstr = '#'
    for val in rgbvals:
        try:
            val = hex(int(val)).replace('0x','')
        except TypeError:
            print('Could not convert ' + val + ' to hex value')
            sys.exit(-1)
        hexstr += val
    return hexstr

def _update_xaxes(fig, title='', xrange=None, xnticks=20, xangle=0, xfontsize=20, xtickformat=None, xtype='date', col=None, reverse_x=False):
    '''
    Set x-axis properties of a fig.
    tickformat is a formatter like "%YQ%q" to specify how dates should be formatted.
    '''

    if reverse_x:
        # The autorange='reversed' option doesn't seem to
        # allow specifying the range.
        # fig.update_xaxes(autorange='reversed', col=col)
        # so swap the xrange manually
        xrange = (xrange[1], xrange[0])
        
    fig.update_xaxes(title_text=title,
                     title_font_size=24,
                     title_font_color='grey',
                     tickfont_size=xfontsize,
                     tickangle=xangle,
                     tickformat=xtickformat,
                     # range
                     range=xrange,
                     # border line
                     showline=True,
                     linewidth=2,
                     linecolor='white',
                     mirror=True,
                     # grid
                     showgrid=True,
                     gridwidth=1,
                     gridcolor='grey',
                     # ticks
                     ticks='inside',
                     nticks=xnticks,
                     tickcolor='white',
                     ticklen=10,
                     type=xtype,
                     col=col)

    return fig

def _update_yaxes(fig, title='', yrange=None, ynticks=10,
                  yangle=0, yfontsize=20,
                  row=1, col=1, secondary_y=False,
                  logy=False):
    '''
    Set y-axis properties of a fig
    '''

    # Set log scale if specified
    if logy:
        ytype = 'log'
    else:
        ytype = 'linear'

    fig.update_yaxes(title_text=title,
                     title_font_size=24,
                     title_font_color='grey',
                     tickfont_size=yfontsize,
                     tickangle=yangle,
                     # which y-axis
                     row=row,
                     col=col,
                     secondary_y=secondary_y,
                     # range
                     range=yrange,
                     # border line
                     showline=True,
                     linewidth=2,
                     linecolor='white',
                     mirror=True,
                     # grid
                     showgrid=True,
                     gridwidth=1,
                     gridcolor='grey',
                     # ticks
                     ticks='inside',
                     nticks=ynticks,
                     tickcolor='white',
                     ticklen=10,
                     type=ytype)

    return fig

def _parse_cols(cols, df):
    '''
    Utility function to parse linecols input to
    create_fig.
    '''

    # Parse list ccols to get which columns to use.
    # These will be saved in use_cols.
    use_cols = []
    
    # If None is given, don't add anything
    if cols is None:
        pass

    # If a str was given, check whether such a column exists and add it.
    elif type(cols) == str:
        if cols not in df.columns:
            print('Column ' + str(cols) + ' does not exist in df:')
            print(df.columns)
            sys.exit(-1)
        use_cols.append(cols)
            
    # If an int is given, check whether it is a valid column index and add it.
    elif type(cols) == int:
        if cols < -len(df.columns) or len(df.columns) <= cols:
            print('Only ' + str(len(df.columns)) + ' columns available, cannot specify cols = ' + str(cols))
            print('Note that columns are 0-based, so first column should be specified as 0')
            sys.exit(-1)
        use_cols.append(df.columns[cols])
            
    # If an iterable is given, check whether valid and add.
    else:
        try:
            for col in cols:
                if type(col) == int:
                    if col < -len(df.columns) or len(df.columns) <= col:
                        print('Only ' + str(len(df.columns)) + ' columns available, cannot specify col ' + str(col))
                        print('Note that columns are 0-based, so first column should be specified as 0')
                        sys.exit(-1)
                    use_cols.append(df.columns[col])
                elif type(col) == str:
                    if col not in df.columns:
                        print('Cannot specify col ' + str(col) + ', does not exist in df:')
                        print(df.columns)
                        sys.exit(-1)
                    use_cols.append(col)
                else:
                    print('cols must be given as list of str or int,')
                    print('given col of type ' + str(type(col)) + ':')
                    print(col)
                    sys.exit(-1)
        except TypeError:
            print('_parse_cols: cols must be given as str, int or iterable of str or int,')
            print('given type of ' + str(type(cols)) + ':')
            print(cols)
            sys.exit(-1)

    # Remove any duplicate columns
    # (using a dict in Python 3.7 onwards will guarantee original ordering)
    use_cols = list(dict.fromkeys(use_cols))

    return use_cols

def _parse_xrange(xrange, df, add_margins=True):
    '''
    Utility function to parse xrange input.
    Returns a tuple of beginning and ending times.
    
    add_margins will add half a period before and after the specified values
    if the axis is a date type.
    '''

    # Make sure index of df is sorted so that
    # df.index[0] is minimum value and
    # df.index[-1] is maximum value.
    df = df.sort_index().copy()

    # If None, show full range of data
    if xrange is None:
        xrange = (df.index[0], df.index[-1])
    # If a number is given, show that many periods from the end
    elif type(xrange) == int:
        if len(df) >= xrange:
            xrange = (df.index[-xrange], df.index[-1])
        else:
            print('WARNING: _parse_xrange():')
            print('xrange given as ' + str(xrange) + ' but df has only length of ' + str(len(df)) + ',')
            print('showing only ' + str(len(df)) + ' periods.')
            print('To show a definite range use for example')
            print('  xrange=("2008-03:2020-03")')
            print('  xrange=("2008-03:")')
            print('  xrange=(":2020-03")')
            print('or')
            print('  xrange=("-5:3")')
            xrange = (df.index[0], df.index[-1])
    # If a str is given, assume it is in format [start]:[end]
    # where [start] and [end] can be interpreted as dates.
    elif type(xrange) == str:
        if xrange.find(':') == -1:
            print('If xrange is str, must be of format [start]:[end]')
            print('xrange: "' + str(xrange) + '"')
            sys.exit(-1)
        try:
            start, end = xrange.split(':')
            start = start.strip()
            end   = end.strip()
        except ValuError:
            print('Could not split ' + str(xrange) + ' into start, end')
            sys.exit(-1)

        # Interpret start, end as values.
        # If start or end is abbreviated, use start, end of df
        if start == '':
            start = df.index[0]
        else:
            try:
                start = float(start)
            except (ValueError, TypeError):
                try:
                    start = pd.Timestamp(start)
                except ValueError:
                    print('Could not interpret start ' + start + ' as date or float')
                    sys.exit(-1)

        if end == '':
            end = df.index[-1]
        else:
            try:
                end = float(end)
            except (ValueError, TypeError):
                try:
                    end = pd.Timestamp(end)
                except ValueError:
                    print('Could not interpret start ' + end + ' as date or float')
                    sys.exit(-1)
                    
        xrange = (start, end)
    # If an iterable of length 2 is given, interpret as dates or periods
    else:
        try:
            xlen = len(xrange)
        except TypeError:
            print('xrange must be None (default), int, str or two values of periods or dates')
            sys.exit(-1)

        if xlen != 2:
            print('xrange must be None (default), int, str or two values of periods or dates')
            sys.exit(-1)

        # If we got two values, interpret these as  dates or values
        x1, x2 = xrange
        try:
            x1 = float(x1)
        except (ValueError, TypeError):
            try:
                x1 = pd.Timestamp(x1)
            except ValueError:
                print('Could not interpret ' + str(x1) + ' as date or float')
        
        try:
            x2 = float(x2)
        except (ValueError, TypeError):
            try:
                x2 = pd.Timestamp(x2)
            except ValueError:
                print('Could not interpret ' + str(x1) + ' as date or float')
                sys.exit(-1)
        # Set xrange if values
        xrange = (x1, x2)
    # end of iterable of length 2

    # Add margins at beginning and end
    # corresponding to half of a period.
    # This *assumes* the data has equally separated index values.
    if type(xrange[0]) == pd.Timestamp and add_margins:
        if len(df) > 1:
            diff = (df.index[1] - df.index[0]) / 2.
            xrange = (xrange[0] - diff, xrange[1] + diff)

    return xrange

def _parse_yrange(yrange, df):
    '''
    Utility function to parse yrange input.
    Returns a tuple of ymin, ymax.

    xrange should be output of _parse_xrange which
    returns tuple of dates for beginning and end.

    Input can be one of
    - None        Return None, no calculation done.
    - (y1, y2)    Returns provided values y1, y2.
                  If either is None, this side will default to available value in df.
    - (x1, x2)    Returns the min/max value of df within range of x1 to x2.
                  if either is None, this side will default to all available values in df.index.
    '''

    # If None just return None
    if yrange is None:
        yrange = None
    # If an iterable of length 2 is given, interpret as dates or periods
    else:
        try:
            ylen = len(yrange)
        except TypeError:
            print('yrange must be None (default), int or two values of periods or dates')
            print('yrange = ' + str(yrange))
            sys.exit(-1)

        if ylen != 2:
            print('yrange must be None (default) or two values of ymin/ymax or xmin/xmax')
            sys.exit(-1)

        # If we got two values, interpret these as periods or dates
        y1, y2 = yrange
        # Try to convert to float, if it works, use as values
        try:
            y1 = float(y1)
            y2 = float(y2)
            yrange = (y1, y2)
        except ValueError:
            # Try to convert to dates, if it works, get min/max in this range
            if y1 is None:
                x1 = df.index[0]
            else:
                try:
                    x1 = pd.Timestamp(y1)
                except ValueError:
                    print('Could not convert ' + str(y1) + ' to pd.Timestamp()')
                    sys.exit(-1)

            # Try to convert to dates, if it works, get min/max in this range
            if y2 is None:
                x2 = df.index[-1]
            else:
                try:
                    x2 = pd.Timestamp(y2)
                except ValueError:
                    print('Could not convert ' + str(y2) + ' to pd.Timestamp()')
                    sys.exit(-1)

            # Get min, max values in range of x1 to x2
            y1 = df.loc[str(x1):str(x2)].min().min()
            y2 = df.loc[str(x1):str(x2)].max().max()
            # Set yrange
            yrange = (y1, y2)
        # end of try to convert y1, y2 to float
    # end of iterable of length 2

    return yrange

def _update_hover(fig, spikex=False, spikey=False):
    '''
    Set hover properties.
    '''

    fig.update_layout(
        # Set hovermode so all values along x are shown
        hovermode='x unified',
        hoverlabel_align = 'right',
        # Format hover box
        hoverlabel={'bgcolor'     : "rgba(255,255,255,0.3)",
                    'font_size'   : 16,
                  # 'font_family' : "Rockwell"
        }
    )

    # Spike lines which show horizontal/vertical lines on cursor
    if spikex:
        fig.update_xaxes(showspikes=True, spikecolor="grey", spikesnap="cursor", spikemode="across")
    if spikey:
        fig.update_yaxes(showspikes=True, spikecolor="grey", spikethickness=1)
    if spikex or spikey:
        fig.update_layout(spikedistance=1000, hoverdistance=100)
    
    return fig

def _add_range_slider(fig, xrange=None, col=None):
                      
    '''
    Add range slider to bottom of chart.
    See https://plotly.com/python/time-series/
    '''

    # Create range slider
    if xrange is None:
        range = None
    else:
        range = xrange

    rangeslider = {'visible'   : True,
                   'autorange' : True,
                   'range'   : range
    }

    if col is None:
        col = 1
    elif col in [1, 2]:
        col = col
    else:
        print('Cannot have col of ' + str(col))
        sys.exit(-1)
        
    fig.update_xaxes(
        rangeslider=rangeslider,
        col=col
    )

    return fig

def _add_range_buttons(fig, stops=['6m', 'YTD', '5y'], no_all=False,
                       xrange=None, col=None):
    '''
    Add range buttons to top of chart.
    Only works with x-axes that are of type "date".
    See https://plotly.com/python/time-series/

    By default, "all" is included regardless of what stops are included.
    To disable specify no_all=True.
    Valid stops are of the format
    - "YTD"
    - "6m"  - specify number of months
    - "3q"  - specify number of quarters
    - "5y"  - specify number of years

    Something wrong with rangeselector for lines+markers, see
    https://github.com/plotly/plotly.js/issues/2209
    For this reason use custom "all" option with range specified by data.
    '''

    # Parse stops and add to list of buttons
    buttonlist = []
    for stop in stops:
        if type(stop) != str:
            print('stop of ' + str(stop) + ' given, cannot parse')
            sys.exit(-1)
        
        if stop.strip().upper() == 'YTD':
            buttonlist.append({'count' : 1, 'label' : 'YTD', 'step' : 'year', 'stepmode' : 'todate'})
        else:
            stop = stop.strip().lower()
            if stop.endswith('m'):
                try:
                    months = int(stop.replace('m', ''))
                    buttonlist.append({'count' : months, 'label' : str(months)+'M', 'step' : 'month', 'stepmode' : 'backward'})
                except ValueError:
                    print('stop of ' + str(stop) + ' given, cannot parse')
                    sys.exit(-1)
            elif stop.endswith('q'):
                try:
                    quarters = int(stop.replace('q', ''))
                    buttonlist.append({'count' : quarters, 'label' : str(quarters)+'Q', 'step' : 'quarter', 'stepmode' : 'backward'})
                except ValueError:
                    print('stop of ' + str(stop) + ' given, cannot parse')
                    sys.exit(-1)
            elif stop.endswith('y'):
                try:
                    years = int(stop.replace('y', ''))
                    buttonlist.append({'count' : years, 'label' : str(years)+'Y', 'step' : 'year', 'stepmode' : 'backward'})
                except ValueError:
                    print('stop of ' + str(stop) + ' given, cannot parse')
                    sys.exit(-1)
            else:
                print(stop + ' is not a valid stop for a rangeselector')
                sys.exit(-1)

    if not no_all:
        # This seems to screw up the range and add way too much margin
        # buttonlist.append({'step' : 'all'})
        #
        # Create myself - get the number of days in data
        days = (xrange[1] - xrange[0]).days
        buttonlist.append({'count' : days, 'label' : 'all', 'step' : 'day', 'stepmode' : 'backward'})

    # Specify x-axis range if given
    if xrange is None:
        range = None
    else:
        range = xrange

    # Specify x position based on columns
    if col in [None, 1]:
        x = 0
    elif col == 2:
        x = 0.52
    else:
        print('Cannot specify x of ' + str(x))
        sys.exit(-1)

    # Create range buttons
    rangebuttons = {'buttons' : buttonlist,
                    'x'       : x,
                    'xanchor' : 'left',
                    'y'       : 1.20,
                    'yanchor' : 'bottom'}
    
    if col is None:
        col = 1
    elif col in [1, 2]:
        col = col
    else:
        print('Cannot have col of ' + str(col))
        sys.exit(-1)
        
    fig.update_xaxes(
        rangeselector=rangebuttons,
        type='date',
        col=col
    )

    return fig

def add_segment(x0, y0, x1, y1,
                fig,
                # Use default "skip" to not show hover info,
                # otherwise it will be shown.
                hover='skip',
                # hover_prec is ignored if hover is "skip"
                hover_prec=1,
                color='red',
                width=3,
                dash='solid',
                col=None, row=None,
                debug=False):
    '''
    Add a line segment to an existing fig.
    Specify the coordinates with x0, y0, x1, y1.
    '''

    # Create DataFrame
    _df = pd.DataFrame({'x' : [x0, x1], 'y' : [y0, y1]}).set_index('x')

    if debug:
        print('-' * 20)
        print('start of add_segment with _df:')
        print(_df)

            
    # Get color if specified
    _dict_colors = {'color' : color, 'width' : width, 'dash' : dash}
    _dict_markers={'opacity' : 0, 'size' : 0}
    showlegend = False

    # Check hover_prec can be interpreted as int
    try:
        hover_prec = int(hover_prec)
        # Convert to str
        hover_prec = str(hover_prec)
    except (TypeError, ValueError):
        print('add_segment(): hover_prec must be interpretable as int')
        sys.exit(-1)
    # Set default hovertemplate
    hovertemplate = str(col)+': %{y:.' + hover_prec + 'f}<extra></extra>'
            
    # Get hover info for this col
    if hover == 'skip':
        hoverinfo = hover
        hovertemplate = None
    else:
        # default is to show legend entry
        hoverinfo = 'all'
            
    # Add trace
    fig.add_trace(
        go.Scatter(x=_df.index, y=_df['y'],
                   mode='lines',
                   line=_dict_colors,
                   marker=_dict_markers,
                   showlegend=showlegend,
                   hoverinfo=hoverinfo,
                   hovertemplate=hovertemplate),
        col=col, row=row)
    
    return fig

def create_fig_2col(df,
                    figtitle=['', ''],
                    legend_title='',
                    
                    # -----------------------------------------------------------
                    # Colors of each trace, keys are column names
                    # and values are dicts like
                    # {'color' : 'rgba(200,100,100,0.8)', 'dash' : 'dash', 'width' : 1}
                    dict_colors={},
                    # Markers for each line trace, keys are column names
                    # and values are dicts like
                    # {'size' : 1, 'opacity' : '0.8'}
                    # Set {'opacity' : 0} to make plots with no markers.
                    dict_markers={},
                    # Legend for each line trace, keys are column names
                    # and values are True/False.
                    dict_legends={},
                    # Whether to show hover for a given column.
                    # Default is 'all' for all objects (except for fill),
                    # specify as 'skip' to not include in hover.
                    dict_hover={},
                    # -----------------------------------------------------------
                    # columns to draw as lines
                    linecolslist=[0,1],
                    # subplots options
                    horizontal_spacing=0.075,
                    column_titles=['', ''],
                    # -----------------------------------------------------------
                    # legend options
                    showlegend=True,
                    # Show a group name for each legend group,
                    # one for left/right chart left/right y-axis.
                    legend_group_names = [None, None, None, None],
                    # -----------------------------------------------------------
                    # Add any additional info that can be extracted
                    # with interactions as customdata.
                    # This can be specified for each col and must  have
                    # the same length as the DataFrame being passed in.
                    dict_customdata={},
                    # -----------------------------------------------------------
                    # x-axis options
                    xtitle='',
                    xnticks=5, # half of full width chart
                    xrange=None,
                    # Option to specify x-axis type, valid options are
                    # - (default, auto), linear, log, date, category, multicategory.
                    xtype='-',
                    xfontsize=20,
                    xangle=0,
                    xhoverformat=None,
                    reverse_x=[False, False],
                    add_xmargins=True,
                    xtickformat=None,
                    # -----------------------------------------------------------
                    # y-axis options
                    ytitle=None,
                    ynticks=10,
                    yrangelist=[None, None, None, None],
                    yfontsize=20,
                    yangle=0,
                    logy=False,
                    # -----------------------------------------------------------
                    # whether x-axis or y-axis is shared between subplots
                    # (default False).
                    # Warnings:
                    # 1. These options do not work when range_slider=True.
                    # 2. sharex does not seem to work for date x-axes.
                    sharex=False,
                    sharey=False,
                    # -----------------------------------------------------------
                    # horizontal/vertical lines/rects
                    hlines=[],
                    vlines=[],
                    hrects=[],
                    vrects=[],
                    # -----------------------------------------------------------
                    # hover options
                    hover_prec = 1,
                    # -----------------------------------------------------------
                    # spike (crosshair) options
                    crosshair=False,
                    # -----------------------------------------------------------
                    # figure options
                    width=1500,
                    height=800,
                    margin_left=80,
                    margin_right=60,
                    margin_top=50,
                    margin_bottom=100,
                    range_buttons=False,
                    range_slider=False,
                    debug=False):
    '''
    Create and return a fig using a df and a list of columns to chart.
    linecolslist must be a list of 2 or 4 elements.
    Provide None as element if the axis is not to be used.
    '''

    if debug:
        print('-' * 20)
        print('start of create_fig_2col with df:')
        print(df[-10:])
        print('linecolslist = ' + str(linecolslist))


    try:
        nitems = len(linecolslist)
    except TypeError:
        print('Cannot get len() of linecolslist: ' + str(linecolslist))
        print('linecolslist must be iterable of length 2 or 4')
        sys.exit(-1)
    if nitems not in [2, 4]:
        print('Number of elements for linecolslist must be 2 or 4, given ' + str(len(nitems)))
        sys.exit(-1)

    # Use left y-axes only
    line_cols = [[], [], [], []]
    if nitems == 2:
        line_cols[0] = _parse_cols(linecolslist[0], df)
        line_cols[2] = _parse_cols(linecolslist[1], df)
    # Use left and right y-axes
    else:
        for i in range(4):
            line_cols[i] = _parse_cols(linecolslist[i], df)

    if debug:
        for i in range(4):
            print('line_cols[' + str(i) + ']:')
            print('\n'.join(line_cols[i]))

    # Get length of each line_cols
    len_line_cols = np.array([len(line_cols[i]) for i in range(4)])

    # Update fig titles.
    # If a str is given, set it to be for both
    try:
        _figtitle1, _figtitle2 = figtitle
    except ValueError:
        print('figtitle must be str or iterable of length 2, given')
        print(figtitle)
        sys.exit(-1)
        
    fig = None
    # If all len_line_cols are 0, no lines to draw, return None for fig
    if np.all(len_line_cols == 0):
        print('WARNING: All line_cols have 0 length, returning None')
        return fig
    # If there is something to show on both right y-axes
    elif len_line_cols[1] == 0 and len_line_cols[3] == 0:
        fig = make_subplots(rows=1, cols=2,
                            specs=[[{"secondary_y": False}, {"secondary_y": False}]],
                            horizontal_spacing=horizontal_spacing,
                            column_titles=column_titles,
                            subplot_titles=figtitle,
                            shared_xaxes=sharex, shared_yaxes=sharey)
    # If there is something to show on left column, right y-axis only
    elif len_line_cols[1] != 0 and len_line_cols[3] == 0:
        fig = make_subplots(rows=1, cols=2,
                            specs=[[{"secondary_y": True}, {"secondary_y": False}]],
                            horizontal_spacing=horizontal_spacing,
                            column_titles=column_titles,
                            subplot_titles=figtitle,
                            shared_xaxes=sharex, shared_yaxes=sharey)
    # If there is something to show on right column, right y-axis only
    elif len_line_cols[1] == 0 and len_line_cols[3] != 0:
        fig = make_subplots(rows=1, cols=2,
                            specs=[[{"secondary_y": False}, {"secondary_y": True}]],
                            horizontal_spacing=horizontal_spacing,
                            column_titles=column_titles,
                            subplot_titles=figtitle,
                            shared_xaxes=sharex, shared_yaxes=sharey)
    else:
        fig = make_subplots(rows=1, cols=2,
                            specs=[[{"secondary_y": True}, {"secondary_y": True}]],
                            horizontal_spacing=horizontal_spacing,
                            column_titles=column_titles,
                            subplot_titles=figtitle,
                            shared_xaxes=sharex, shared_yaxes=sharey)

    # Adjust margins
    fig.update_layout(margin=dict(l=margin_left, r=margin_right, t=margin_top, b=margin_bottom))

    # If sharey was specified, make sure y-axis ticks are shown in right subplot
    fig.update_layout(yaxis2_showticklabels=True)

    # Check hover_prec can be interpreted as int
    try:
        hover_prec = int(hover_prec)
        # Convert to str
        hover_prec = str(hover_prec)
    except (TypeError, ValueError):
        print('add_segment(): hover_prec must be interpretable as int')
        sys.exit(-1)

    # Check legend group names
    if len(legend_group_names) != 4:
        print('legend_group_names must be a list of 4 items,')
        print('for left chart left y-axis, left chart right y-axis,')
        print('right chart left y-axis, right chart right y-axis.')
        sys.exit(-1)
    
    # Loop over each line_cols
    for i in range(4):
        for icol, col in enumerate(line_cols[i]):
            if col not in df.columns:
                print('Column ' + str(col) + ' not found in df:')
                print(df[-5:])
                sys.exit(-1)

            if debug:
                print('adding col ' + str(col))

            # Get line color if specified
            if col in dict_colors:
                _dict_colors = dict_colors[col]
            else:
                _dict_colors = {}

            # Get marker if specified
            if col in dict_markers:
                _dict_markers = dict_markers[col]
            else:
                _dict_markers = {}

            # Get legend info for this col
            if col in dict_legends:
                _showlegend = dict_legends[col]
            else:
                # default is to show legend entry
                _showlegend = True

            # Set default hovertemplate
            hovertemplate = str(col)+': %{y:.' + hover_prec + 'f}<extra></extra>'

            # Add any customdata if it is specified for this col
            if col in dict_customdata:
                customdata = dict_customdata[col]
            else:
                customdata = None
            
            # Get hover info for this col
            if col in dict_hover:
                hoverinfo = dict_hover[col]
                if hoverinfo in ['skip', 'none']:
                    hovertemplate = None
            else:
                # default is to show legend entry
                hoverinfo = 'all'

            # If first column for this y-axis, add legend group name
            if icol == 0:
                _legend_group_name = legend_group_names[i]
            else:
                _legend_group_name = None
                
            # Left column, left y-axis
            if i == 0:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[col],
                               mode='lines+markers',
                               name=col,
                               line=_dict_colors,
                               marker=_dict_markers,
                               showlegend=_showlegend,
                               legendgroup="group1",
                               legendgrouptitle_text=_legend_group_name,
                               hoverinfo=hoverinfo,
                               hovertemplate=hovertemplate,
                               customdata=customdata,
                               legendrank=i*100 + icol+1,
                               ),
                    row=1, col=1, secondary_y=False,
                )
            # Left column, right y-axis
            elif i == 1:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[col],
                               mode='lines+markers',
                               name=col,
                               line=_dict_colors,
                               marker=_dict_markers,
                               showlegend=_showlegend,
                               legendgroup="group2",
                               legendgrouptitle_text=_legend_group_name,
                               hoverinfo=hoverinfo,
                               hovertemplate=hovertemplate,
                               customdata=customdata,
                               legendrank=i*100 + icol+1,
                               ),
                    row=1, col=1, secondary_y=True,
                    )
            # Right column, left y-axis
            elif i == 2:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[col],
                               mode='lines+markers',
                               name=col,
                               line=_dict_colors,
                               marker=_dict_markers,
                               showlegend=_showlegend,
                               legendgroup="group3",
                               legendgrouptitle_text=_legend_group_name,
                               hoverinfo=hoverinfo,
                               hovertemplate=hovertemplate,
                               customdata=customdata,
                               legendrank=i*100 + icol+1,
                               ),
                    row=1, col=2, secondary_y=False,
                    )
            # Right column, right y-axis
            elif i == 3:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[col],
                               mode='lines+markers',
                               name=col,
                               line=_dict_colors,
                               marker=_dict_markers,
                               showlegend=_showlegend,
                               legendgroup="group4",
                               legendgrouptitle_text=_legend_group_name,
                               hoverinfo=hoverinfo,
                               hovertemplate=hovertemplate,
                               customdata=customdata,
                               legendrank=i*100 + icol+1,
                               ),
                    row=1, col=2, secondary_y=True,
                )
    # Set width, height of fig
    fig.update_layout(width=width, height=height,
                      dragmode='pan')

    if xtype != '-':
        fig.update_xaxes(type=xtype)

    if xtype not in ['-', 'date']:
        # Also turn off range_buttons
        range_buttons = False

    xrange = _parse_xrange(xrange, df, add_margins=add_xmargins)
        
    for icol, col in enumerate([1, 2]):
        fig = _update_xaxes(fig, title=xtitle,
                            xrange=xrange,
                            xnticks=xnticks,
                            xangle=xangle,
                            xfontsize=xfontsize,
                            xtickformat=xtickformat,
                            xtype=xtype,
                            reverse_x=reverse_x[icol],
                            col=col)

    # Set y-axis ranges
    # If logy option is length 2, this is for left and right chart.
    try:
        logy_l, logy_r = logy
    except TypeError:
        logy_l = logy
        logy_r = logy
        
    # Left chart left y-axis
    yrange = _parse_yrange(yrangelist[0], df[line_cols[0]])
    fig = _update_yaxes(fig, title=ytitle,
                        yrange=yrange,
                        ynticks=ynticks,
                        yangle=yangle,
                        yfontsize=yfontsize,
                        col=1, secondary_y=False,
                        logy=logy_l)
    
    # Left chart right y-axis
    yrange = _parse_yrange(yrangelist[1], df[line_cols[1]])
    fig = _update_yaxes(fig, title=ytitle,
                        yrange=yrange,
                        ynticks=ynticks,
                        yangle=yangle,
                        yfontsize=yfontsize,
                        col=1, secondary_y=True,
                        logy=logy_l)

    # Right chart left y-axis
    yrange = _parse_yrange(yrangelist[2], df[line_cols[2]])
    fig = _update_yaxes(fig, title=ytitle,
                        yrange=yrange,
                        ynticks=ynticks,
                        yangle=yangle,
                        yfontsize=yfontsize,
                        col=2, secondary_y=False,
                        logy=logy_r)
    
    # Right chart right y-axis
    yrange = _parse_yrange(yrangelist[3], df[line_cols[3]])
    fig = _update_yaxes(fig, title=ytitle,
                        yrange=yrange,
                        ynticks=ynticks,
                        yangle=yangle,
                        yfontsize=yfontsize,
                        col=2, secondary_y=True,
                        logy=logy_r)

    # Add hlines, vlines, hrects, vrects
    for _hline in hlines:
        fig = add_hline(fig, _hline)
    for _vline in vlines:
        fig = add_vline(fig, _vline)
    for _hrect in hrects:
        fig = add_hrect(fig, _hrect)
    for _vrect in vrects:
        fig = add_vrect(fig, _vrect)

    # Set legend
    if showlegend:
        fig.update_layout(legend={# 'xanchor' : "left",
                                  # 'yanchor' : "bottom",
                                  # 'x'       : 0.02,
                                  # 'y'       : 1.02,
                                  # 'orientation' : 'h',
                                  'bgcolor' : 'white',
                                  'bordercolor' : 'white',
                                  'borderwidth' : 2,
                                  # Set to "grouped" for create_fig_2col()
                                  'traceorder'  :'grouped',
                                  # Available starting in plotly version 5.3:
                                  # For behavior when clicking on legend of a grouped item.
                                  # "toggleitem" will only toggle that item,
                                  # "togglegroup" will toggle all items in the group.
                                  # 'groupclick' : 'toggleitem',
                                  'font' : {# 'family' : 'Courier',
                                      'size'   : 16,
                                      'color'   : 'black'},
                                  },
                          legend_title_text=legend_title,
                          # Separate legends are not possible for 2-col charts,
                          # so set gap between.
                          # See
                          # https://www.kaggle.com/code/jrmistry/plotly-how-to-make-individual-legends-in-subplot/notebook
                          legend_tracegroupgap = 50,
        )
    else:
        fig.update_layout(showlegend=False)
        
    # Set hover
    fig = _update_hover(fig)

    # Add range selector
    if range_buttons:
        fig = _add_range_buttons(fig, xrange=xrange, col=1)
        fig = _add_range_buttons(fig, xrange=xrange, col=2)
    if range_slider:
        fig = _add_range_slider(fig, xrange=xrange, col=1)
        fig = _add_range_slider(fig, xrange=xrange, col=2)

    # Adjust xhoverformat
    if xhoverformat is not None:
        fig.update_traces(xhoverformat=xhoverformat)
    
    # Add crosshair (spike) if specified.
    # No need to specify col, seems to apply to both.
    if crosshair:
        fig.update_xaxes(showspikes=True, spikecolor="rgba(50,50,50,0.7)",
                         spikethickness=1, spikesnap="cursor", spikemode="across", spikedash='dash')
        fig.update_yaxes(showspikes=True, spikecolor="rgba(50,50,50,0.7)",
                         spikethickness=1, spikesnap="cursor", spikemode="across", spikedash='dash')
        fig.update_layout(spikedistance=1000, hoverdistance=100)
            
    return fig

def add_lines(df,
              fig=None,
              # -----------------------------------------------------------
              # Colors of each trace
              dict_colors={},
              dict_markers={},
              dict_legends={},
              dict_hover={},
              # -----------------------------------------------------------
              # columns to draw as lines
              linecols='all',
              rlinecols=None,
              # -----------------------------------------------------------
              # Add any additional info that can be extracted
              # with interactions as customdata.
              # This must have the same length as the DataFrame being passed in.
              dict_customdata={},
              # Option to create right y-axis in case it is used later
              right_yaxis=False,
              hover_prec=1,
              # Specify row, col (use underscore to not confuse with column names)
              row=1, col=1,
              debug=False):
    '''
    Create a fig using a df and a list of columns for lines.
    If no line_cols are given, None is returned.
    '''

    # Copy args row, col to be rownum, colnum
    # so it is not confused with any column names.
    rownum = row
    colnum = col

    # If df was type Series, convert to DataFrame
    if type(df) == pd.Series:
        df = pd.DataFrame(df)

    if debug:
        print('-' * 20)
        print('start of add_lines with df:')
        print(df[-10:])
        print('linecols = ' + str(linecols))

    # Parse input cols
    line_cols = _parse_cols(linecols, df)
    rline_cols = _parse_cols(rlinecols, df)
    if debug:
        print('line_cols:')
        print('\n'.join(line_cols))

        print('rline_cols:')
        print('\n'.join(rline_cols))
        
    if fig is None:
        # If any rline_cols were specified, set up to have right y-axis
        if len(rline_cols) > 0 or right_yaxis:
            if debug:
                print('setting secondary_y to True')
            fig = make_subplots(specs=[[{'secondary_y' : True}]])
        # Otherwise don't specify right y-axis
        else:
            fig = make_subplots()

    # Add traces for line_cols
    for icol, col in enumerate(line_cols):
        # Check that col exists in df
        if col not in df.columns:
            print('Column ' + str(col) + ' not found in df:')
            print(df[-5:])
            sys.exit(-1)
            
        if debug:
            print('adding col ' + str(col))
            
        # Get color if specified
        if col in dict_colors:
            _dict_colors = dict_colors[col]
        else:
            _dict_colors = {}

        # Get marker if specified
        if col in dict_markers:
            _dict_markers = dict_markers[col]
        else:
            _dict_markers = {}

        # Get legend info for this col
        if col in dict_legends:
            showlegend = dict_legends[col]
        else:
            # default is to show legend entry
            showlegend = True

        # Check hover_prec can be interpreted as int
        try:
            hover_prec = int(hover_prec)
            # Convert to str
            hover_prec = str(hover_prec)
        except (TypeError, ValueError):
            print('add_segment(): hover_prec must be interpretable as int')
            sys.exit(-1)
        # Set default hovertemplate
        hovertemplate = str(col)+': %{y:.' + hover_prec + 'f}<extra></extra>'            
            
        # Get hover info for this col
        if col in dict_hover:
            hoverinfo = dict_hover[col]
            if hoverinfo in ['skip', 'none']:
                hovertemplate = None
            print('*' * 30)
            print('hoverinfo = ' + hoverinfo)
            print('*' * 30)
        else:
            # default is to show legend entry
            hoverinfo = 'all'

        # Add any customdata if it is specified for this col
        if col in dict_customdata:
            customdata = dict_customdata[col]
        else:
            customdata = None
            
        fig.add_trace(
            go.Scatter(x=df.index, y=df[col],
                       mode='lines+markers',
                       showlegend=showlegend,
                       hoverinfo=hoverinfo,
                       customdata=customdata,
                       name=col,
                       line=_dict_colors,
                       marker=_dict_markers,
                       hovertemplate = hovertemplate,
                       legendrank=icol+1),
            row=rownum, col=colnum
        )

    # Add traces for rline_cols
    for icol, col in enumerate(rline_cols):
        # Check that col exists in df
        if col not in df.columns:
            print('Column ' + str(col) + ' not found in df:')
            print(df[-5:])
            sys.exit(-1)
            
        if debug:
            print('adding col ' + str(col))

        # Get color if specified
        if col in dict_colors:
            _dict_colors = dict_colors[col]
        else:
            _dict_colors = {}

        # Get marker if specified
        if col in dict_markers:
            _dict_markers = dict_markers[col]
        else:
            _dict_markers = {}

        # Get legend info for this col
        if col in dict_legends:
            showlegend = dict_legends[col]
        else:
            # default is to show legend entry
            showlegend = True

        # Get hover info for this col
        if col in dict_hover:
            hoverinfo = dict_hover[col]
        else:
            # default is to show legend entry
            hoverinfo = 'all'
            
        fig.add_trace(
            go.Scatter(x=df.index, y=df[col],
                       mode='lines+markers',
                       showlegend=showlegend,
                       hoverinfo=hoverinfo,
                       customdata=customdata,
                       name=col,
                       line=_dict_colors,
                       marker=_dict_markers,
                       hovertemplate=hovertemplate,
                       legendrank=1000+icol+1),
            row=rownum, col=colnum,
            secondary_y=True
        )
                
    return fig

def add_bars(df, barcols,
             fig=None,
             stack=True, bar_right=False,
             barwidth=None,
             dict_colors={},
             dict_patterns={},
             dict_legends={},
             dict_hover={},
             list_barcolors=None,
             opacity=0.3,
             # -----------------------------------------------------------
             # Add any additional info that can be extracted
             # with interactions as customdata.
             # This must have the same length as the DataFrame being passed in.
             dict_customdata={},
             legendrank_offset=0,
             hover_prec=1,
             # Specify row, col (use underscore to not confuse with column names)
             row=1, col=1,
             debug=False):
    '''
    Add stacked bars to existing fig (may be None).
    Stacked bars are added from cols in barcols of df.
    '''

    # Copy args row, col to be rownum, colnum
    # so it is not confused with any column names.
    rownum = row
    colnum = col
    
    # If df was type Series, convert to DataFrame
    if type(df) == pd.Series:
        df = pd.DataFrame(df)

    # Check that cols in barcols exist in df.
    # If a str was given, convert to list.
    if type(barcols) == str:
        barcols = [barcols]
    for col in barcols:
        if col not in df.columns:
            print('Column ' + str(col) + ' not in df:')
            print(df[-5:])
            sys.exit(-1)

    # Create fig if not specified
    if fig is None:
        # If bar_right was specified, set up to have right y-axis
        if bar_right:
            if debug:
                print('setting secondary_y to True')
            fig = make_subplots(specs=[[{'secondary_y' : True}]])
        # Otherwise don't specify right y-axis
        else:
            fig = make_subplots()

    # Add stacked bars
    if stack:
        fig.update_layout(barmode='relative')
    else:
        fig.update_layout(barmode='group')
        
    for icol, col in enumerate(barcols):
        if debug:
            print('adding icol = ' + str(icol) + ' col = ' + str(col))
            print('bar_right = ' + str(bar_right))
            
        if col in dict_colors:
            _dict_colors = dict_colors[col]
        else:
            _dict_colors = {}

        # Get hatches (pattern) for this col
        if col in dict_patterns:
            marker_pattern = dict_patterns[col]
        else:
            marker_pattern = {}
            
        # Get legend info for this col
        if col in dict_legends:
            showlegend = dict_legends[col]
        else:
            # default is to show legend entry
            showlegend = True

        # Check hover_prec can be interpreted as int
        try:
            hover_prec = int(hover_prec)
            # Convert to str
            hover_prec = str(hover_prec)
        except (TypeError, ValueError):
            print('add_segment(): hover_prec must be interpretable as int')
            sys.exit(-1)
        # Set default hovertemplate
        hovertemplate = str(col)+': %{y:.' + hover_prec + 'f}<extra></extra>'            
            
        # Get hover info for this col
        if col in dict_hover:
            hoverinfo = dict_hover[col]
            if hoverinfo in ['skip', 'none']:
                hovertemplate = None
        else:
            # default is to show legend entry
            hoverinfo = 'all'

        # Add any customdata if it is specified for this col
        if col in dict_customdata:
            customdata = dict_customdata[col]
        else:
            customdata = None

        # If no list_barcolors is given, use dict_colors
        if list_barcolors is None:
            fig.add_trace(
                go.Bar(x=df.index, y=df[col], name=col,
                       marker=_dict_colors,
                       marker_pattern=marker_pattern,
                       width=barwidth,
                       showlegend=showlegend,
                       hoverinfo=hoverinfo,
                       customdata=customdata,
                       opacity=opacity,
                       hovertemplate=hovertemplate,
                       legendrank=icol+legendrank_offset+1001),
                row=rownum, col=colnum,
                secondary_y=bar_right
            )
        # If list_barcolors is given, use it
        else:
            fig.add_trace(
                go.Bar(x=df.index, y=df[col], name=col,
                       marker_color=list_barcolors,
                       marker_pattern=marker_pattern,
                       width=barwidth,
                       showlegend=showlegend,
                       hoverinfo=hoverinfo,
                       customdata=customdata,
                       opacity=opacity,
                       hovertemplate=hovertemplate,
                       legendrank=icol+legendrank_offset+1001),
                row=rownum, col=colnum,
                secondary_y=bar_right
            )

    return fig

def add_area(df, area_cols, 
             fig=None,
             bar_right=False,
             dict_colors={},
             # not available as of plotly 5.1.0
             # dict_patterns={},
             dict_legends={},
             dict_hover={},
             opacity=0.3,
             # -----------------------------------------------------------
             # Add any additional info that can be extracted
             # with interactions as customdata.
             # This must have the same length as the DataFrame being passed in.
             dict_customdata={},
             legendrank_offset=0,
             hover_prec=1,
             # Specify row, col (use underscore to not confuse with column names)
             row=1, col=1,
             debug=False):
    '''
    Add stacked bars to existing fig (may be None).
    Stacked bars are added from cols in area_cols of df.
    '''
    global STACKGROUP

    # Copy args row, col to be rownum, colnum
    # so it is not confused with any column names.
    rownum = row
    colnum = col
    
    # If df was type Series, convert to DataFrame
    if type(df) == pd.Series:
        df = pd.DataFrame(df)
    
    # Check that cols in area_cols exist in df
    # If a str was given, convert to list.
    if type(area_cols) == str:
        area_cols = [area_cols]
    for col in area_cols:
        if col not in df.columns:
            print('Column ' + str(col) + ' not in df:')
            print(df[-5:])
            sys.exit(-1)

    # Create fig if not specified
    if fig is None:
        # If bar_right was specified, set up to have right y-axis
        if bar_right:
            if debug:
                print('setting secondary_y to True')
            fig = make_subplots(specs=[[{'secondary_y' : True}]])
        # Otherwise don't specify right y-axis
        else:
            fig = make_subplots()

    # Add area plots
    for icol, col in enumerate(area_cols):
        if debug:
            print('adding icol = ' + str(icol) + ' col = ' + str(col))

        if col in dict_colors:
            _dict_colors = dict_colors[col]
        else:
            _dict_colors = {}

        # not available as of plotly 5.1.0
        ## # Get hatches (pattern) for this col
        ## if col in dict_patterns:
        ##     marker_pattern = dict_patterns[col]
        ## else:
        ##     marker_pattern = {}
            
        # Get legend info for this col
        if col in dict_legends:
            showlegend = dict_legends[col]
        else:
            # default is to show legend entry
            showlegend = True

        # Check hover_prec can be interpreted as int
        try:
            hover_prec = int(hover_prec)
            # Convert to str
            hover_prec = str(hover_prec)
        except (TypeError, ValueError):
            print('add_segment(): hover_prec must be interpretable as int')
            sys.exit(-1)
        # Set default hovertemplate
        hovertemplate = str(col)+': %{y:.' + hover_prec + 'f}<extra></extra>'            
            
        # Get hover info for this col
        if col in dict_hover:
            hoverinfo = dict_hover[col]
            if hoverinfo in ['skip', 'none']:
                hovertemplate = None
        else:
            # default is to show legend entry
            hoverinfo = 'all'

        # Add any customdata if it is specified for this col
        if col in dict_customdata:
            customdata = dict_customdata[col]
        else:
            customdata = None
            
        if icol == 0:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, fill='tozeroy',
                                     line=_dict_colors,
                                     # don't show any lines
                                     mode='none',
                                     # not available as of plotly 5.1.0
                                     # marker_pattern=marker_pattern,
                                     opacity=opacity,
                                     showlegend=showlegend,
                                     hoverinfo=hoverinfo,
                                     customdata=customdata,
                                     # set unique stackgroup
                                     stackgroup=str(STACKGROUP),
                                     hovertemplate=hovertemplate,
                                     legendrank=icol+legendrank_offset+1001),
                          row=rownum, col=colnum,
                          secondary_y=bar_right
            )
        else:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, fill='tonexty',
                                     line=_dict_colors,
                                     # don't show any lines
                                     mode='none',
                                     # not available as of plotly 5.1.0
                                     # marker_pattern=marker_pattern,
                                     opacity=opacity,
                                     showlegend=showlegend,
                                     hoverinfo=hoverinfo,
                                     customdata=customdata,
                                     # set unique stackgroup
                                     stackgroup=str(STACKGROUP),
                                     hovertemplate=hovertemplate,
                                     legendrank=icol+legendrank_offset+1001),
                          row=rownum, col=colnum,
                          secondary_y=bar_right
            )
            
    # Increment global STACKGROUP
    STACKGROUP += 1
    
    return fig

def find_intersect(a, b, pos='prev', debug=False):
    '''
    For two DataFrames, find where two lines intersect
    Each DataFrame should have an index as well as two columns where
    one column has a lower value for the first DataFrame and
    this order is reversed for the other DataFrame.

    Returns a a DataFrame with the same structure as a and b,
    but with the crossing point of the two columns.
    If either DataFrame contains null values, returns None
    '''

    if debug:
        print('start of find_intersect() with pos = ' + pos + ':')
        print('a:')
        print(a)
        print('-' * 40)
        print('b:')
        print(b)

    # Each DataFrame should have col called "__higher__"
    # which contains column name of higher column.
    # Check that __higher__ does not match
    highercol0 = a['__higher__'].values[0]
    highercol1 = b['__higher__'].values[0]
    if highercol0 == highercol1:
        print('Col "__higher__" should not match:')
        print(a)
        print('-' * 10)
        print(b)
        sys.exit(-1)

    # Which value to assign to col "__higher__"
    # depends on whether we are processing the previous or next part
    if pos == 'prev':
        highercol = highercol1
    elif pos == 'next':
        highercol = highercol0
    else:
        print('pos must be prev or next')
        sys.exit(-1)
        
    # Convert index to timestamp
    if type(a.index) == pd.DatetimeIndex:
        x0 = a.index[0].timestamp()
        x1  = b.index[0].timestamp()
    elif type(a.index) in [pd.Int64Index, pd.Float64Index]:
        x0 = a.index[0].timestamp()
        x1  = b.index[0].timestamp()
    else:
        print('Unimplemented index type ' + str(type(a.index)))
        sys.exit(-1)

    # Get 4 values of y
    yhi0 = a[highercol0].values[0]
    ylo0 = a[highercol1].values[0]

    yhi1 = b[highercol1].values[0]
    ylo1 = b[highercol0].values[0]

    # Get intersection point
    x = (yhi0-ylo0) / ((yhi1-ylo1) + (yhi0-ylo0)) * (x1-x0) + x0
    y = ylo0 + (yhi1 - ylo0) / (x1 - x0) * (x - x0)

    if pd.isnull(x) or pd.isnull(y):
        # Return None if a value is missing
        return None

    # Convert back to time if necessary
    if type(a.index) == pd.DatetimeIndex:
        # Due to complications due to timezones,
        # it is better to just add the difference of x-x0 to x,
        # than calculate x directly.
        x = a.index[0] + pd.Timedelta(seconds=x-x0)

    # Create DataFrame in the same format
    indexname = a.index.name
    df_mid = pd.DataFrame({indexname : [x],
                           highercol0 : [y], highercol1 : [y], '__higher__' : [highercol]})
    df_mid.set_index(indexname, inplace=True)

    return df_mid

def split_df(df, hi, lo):
    '''
    Utility function used by add_fill().
    Split df into segments based on where two columns intersect in height.
    Returns a list of DataFrames.
    '''

    df = df.copy()

    # Add a column for which column is higher.
    # This is used when the two columns are alternating in height.
    # Set default "__higher__" to be hi col.
    df['__higher__'] = hi
    # Change for places where lo is higher.
    idx = df[df[hi] <= df[lo]].index
    df.loc[idx, '__higher__'] = lo

    # Split into groups of which is higher
    # and set as list of dfs
    df['group'] = df['__higher__'].ne(df['__higher__'].shift()).cumsum()
    g = df.groupby('group')
    dflist = []
    for igroup, (_, _df) in enumerate(g):
        # Need to interpolate between points.
        # Insert a point between groups where the lines cross,
        # and add to each _df.

        if _df.index.name is not None:
            idxname = _df.index.name
        else:
            idxname = 'index'
        
        # Add the intersection from the last point of the previous group.
        # No need to add start for 0th group.
        if igroup != 0:
            # The key for each group starts at 1,
            # so the previous group is 1 + igroup-1.
            prev_point = g.get_group(1+igroup-1).iloc[[-1]]
            start_point = _df.iloc[[0], :]
            # Find where the points intersect
            intersect = find_intersect(prev_point, start_point, pos='prev')

            # Combine with _df
            if intersect is not None:
                _df = pd.concat([intersect.reset_index(), _df.reset_index()]).set_index(idxname)
            
        # Add the intersection from the first point of the next group.
        # No need to add end for final group
        if igroup != len(g)-1:
            # The key for each group starts at 1,
            # so the next group is 1 + igroup+1.
            next_point = g.get_group(1+igroup+1).iloc[[0]]
            end_point = _df.iloc[[-1], :]
            # Find where the points intersect
            intersect = find_intersect(end_point, next_point, pos='next')

            # Combine with _df
            if intersect is not None:
                _df = pd.concat([_df.reset_index(), intersect.reset_index()]).set_index(idxname)
            
        dflist.append(_df)
    # end of loop over g

    return dflist

def add_fill(df, lo, hi,
             fig=None,
             names=None,
             right_yaxis=False,
             # This should be a single color
             # or a list of 1 or 2 colors.
             colors=['rgba(100,100,200, 0.4)', 'rgba(200,100,100, 0.4)'],
             dict_legends={},
             legendrank_offset=0,
             # Use default "skip" to not show hover info,
             # otherwise it will be shown.
             hover='skip',
             # hover_prec is ignored if hover is "skip"
             hover_prec=1,
             xhoverformat='prev',
             col=1,
             debug=False):
    '''
    Add filled area to existing fig (may be None).
    Specify fig, df, and columns lo and hi.

    Interpolation method based on answer in
    https://stackoverflow.com/questions/64741015/plotly-how-to-color-the-fill-between-two-lines-based-on-a-condition
    
    '''
    global STACKGROUP

    # Check hover_prec can be interpreted as int
    try:
        hover_prec = int(hover_prec)
        # Convert to str
        hover_prec = str(hover_prec)
    except (TypeError, ValueError):
        print('add_segment(): hover_prec must be interpretable as int')
        sys.exit(-1)
    # Set default hovertemplate
    hovertemplate = str(col)+': %{y:.' + hover_prec + 'f}<extra></extra>'
            
    # Get hover info for this col
    if hover == 'skip':
        hoverinfo = hover
        hovertemplate = None
    else:
        # default is to show legend entry
        hoverinfo = 'all'
    
    df = df.copy()
    
    # If df was type Series, convert to DataFrame.
    # Will not work anyway since only one column.
    if type(df) == pd.Series:
        df = pd.DataFrame(df)
    
    # Check that cols in stack_cols exist in df
    if lo not in df.columns:
            print('Column ' + lo + ' not in df:')
            print(df[-5:])
            sys.exit(-1)
    if hi not in df.columns:
            print('Column ' + hi + ' not in df:')
            print(df[-5:])
            sys.exit(-1)

    # Make sure to drop any NA rows as
    # this may add unnecessary points at y=0.
    df = df[[lo, hi]].dropna(axis=0, how='all')
            
    # If names are specified, make sure it is 2 values
    if names is not None:
        try:
            lo_name, hi_name = names
        except TypeError:
            print('add_fill: names must be iterable of length 2, given:')
            print(names)
    else:
        lo_name = lo
        hi_name = hi

    # Add fill area
    if fig is None:
        fig = go.Figure()

    # Split the original df into segments based on where the lines intersect.
    dflist = split_df(df, hi, lo)
    
    def determine_fillcolor(label):
        '''
        Determine which color to use based on
        which column has a higher value.
        '''
        if label == hi:
            if type(colors) == str:
                return colors
            elif type(colors) == list:
                return colors[0]
        elif label == lo:
            if type(colors) == str:
                return colors
            elif type(colors) == list:
                if len(colors) == 1:
                    return colors[0]
                elif len(colors) == 2:
                    return colors[1]
                else:
                    print('colors should be str or list of size 1 or 2')
                    print('Given: ' + str(colors))
                    sys.exit(-1)
        else:
            print('label ' + str(label) + ' is not valid')
            sys.exit(-1)

    # Add traces for each df in dflist:
    for idf, _df in enumerate(dflist):
        _hi = _df['__higher__'].values[0]
        _lo = lo if _hi == hi else hi

        # Deafult is to not show legend, show only if
        # dict_legends is True for the specified col.
        if _lo in dict_legends:
            showlegend = dict_legends[_lo]
        else:
            # default is to *NOT* show legend entry
            showlegend = False
            
        # Low
        # This is just to draw an invisible line that the High line
        # will up to.
        fig = fig.add_trace(go.Scatter(x=_df.index, y =_df[_lo],
                                       line = {'color' : 'rgba(0,0,0,0)'},
                                       fill=None,
                                       fillcolor='rgba(0,0,0,0)',
                                       mode='lines',
                                       opacity=0,
                                       name=lo_name,
                                       showlegend=showlegend,
                                       # set unique stackgroup for this fill
                                       stackgroup=str(STACKGROUP),
                                       hoverinfo=hoverinfo,
                                       hovertemplate=hovertemplate,
                                       legendrank=1+legendrank_offset+1001),
                            row=1, col=col, secondary_y=right_yaxis)

        # Deafult is to not show legend, show only if
        # dict_legends is True for the specified col.
        if _hi in dict_legends:
            showlegend = dict_legends[_hi]
        else:
            # default is to *NOT* show legend entry
            showlegend = False
        
        # High
        # Select fill color.
        fillcolor = determine_fillcolor(_df['__higher__'].values[0])
        # y of fill needs to be difference of the two columns.
        fig = fig.add_trace(go.Scatter(x=_df.index, y =_df[_hi] - _df[_lo],
                                       line={'color' : 'rgba(0,0,0,0)'},
                                       mode='lines',
                                       name=hi_name,
                                       showlegend=showlegend,
                                       fill='tonexty',
                                       fillcolor = fillcolor,
                                       # set to have same stackgroup as above
                                       stackgroup=str(STACKGROUP),
                                       hoverinfo=hoverinfo,
                                       hovertemplate=hovertemplate,
                                       legendrank=0+legendrank_offset+1001),
                            row=1, col=col, secondary_y=right_yaxis)
    
        # Increment global STACKGROUP.
        # This should be common to the two traces above,
        # but need to increment so that other bars are not influenced by these.
        STACKGROUP += 1
        
    # end of loop over dflist

    # Adjust xhoverformat to use previous format if it exists.
    if xhoverformat == 'prev':
        # Try to find a previously set xhoverformat
        xhoverformat = None
        for trace in fig['data']:
            if 'xhoverformat' in trace:
                xhoverformat = trace['xhoverformat']
                break
    elif xhoverformat is not None:
        fig.update_traces(xhoverformat=xhoverformat)
    
    return fig

def add_text(text, x, y,
             fig=None,
             color='black',
             size=20,
             font='Arial',
             textangle=0,
             # use "paper" to use absolute coords
             xref='x',
             yref='y',
             xanchor='left',
             yanchor='top',
             col=None, row=None,
             debug=False):
    '''
    Add text annotation to existing fig (may be None).
    '''

    if fig is None:
        fig = go.Figure()

    # If col is given but no row is given, set row to 1.
    # This allows users to specify col only without having to add row=1.
    if col is not None and row is None:
        row = 1

    # Add color, font, size
    fig.add_annotation(font={'color' : color,
                             'size'  : size,
                             'family' : font},
                       x=x,
                       y=y,
                       showarrow=False,
                       text=text,
                       textangle=textangle,
                       xanchor=xanchor,
                       yanchor=yanchor,
                       xref=xref,
                       yref=yref,
                       col=col,
                       row=row)
    return fig

def create_fig(df,
               figtitle='',
               legend_title='',
               # -----------------------------------------------------------
               # Colors of each trace, keys are column names
               # and values are dicts like
               # {'color' : 'rgba(200,100,100,0.8)', 'dash' : 'dash', 'width' : 1}
               dict_colors={},
               # Markers for each line trace, keys are column names
               # and values are dicts like
               # {'size' : 1, 'opacity' : '0.8'}
               # Set {'opacity' : 0} to make plots with no markers.
               dict_markers={},
               # Hatches (patterns) for each column, keys are column names
               # and values are dicts like
               # {'shape' : '+', 'size' : 3,
               #  'fgcolor' : 'white', 'fgopacity' : 0.5,
               #  'bgcolor' : 'red', '}
               # See
               # https://plotly.com/python-api-reference/generated/plotly.graph_objects.Bar.html#plotly.graph_objects.bar.Marker.pattern
               # for details of options.
               # Available shapes are
               #  "", "/", "\", "x", "-", "|", "+", "."
               # Can be used for bars only (area may be available in newer versions?).
               dict_patterns = {},
               # Legend for each line trace, keys are column names
               # and values are True/False.
               dict_legends={},
               # Whether to show hover for a given column.
               # Default is 'all' for all objects (except for fill),
               # specify as 'skip' to not include in hover.
               dict_hover={},
               # -----------------------------------------------------------
               # Columns for line charts, default is 0th column.
               linecols=0,
               # columns for right y-axis
               rlinecols=None,
               # columns for stacked bars, default is no bars
               barcols=None,
               # -----------------------------------------------------------
               # Bar/Area options
               # by default, stack is True,
               # set to False to get groups of individual bars
               stack=True,
               # Set area to True to get stacked area plot.
               # Will override any stack argument and is always stacked.
               area=False,
               # Bar width.
               # Default is None (plotly will adjust).
               # For time axis, specify in milliseconds.
               barwidth=None,
               # Whether the bars/areas should be on right y-axis
               bar_right=False,
               bar_opacity=0.3,
               # Specify each bar's color as a list
               list_barcolors=None,
               # -----------------------------------------------------------
               # fill options for confidence intervals
               fillcols=None,
               fillright=False,
               fillcolors=None,
               # -----------------------------------------------------------
               # legend options
               showlegend=True,
               # -----------------------------------------------------------
               # Add any additional info that can be extracted
               # with interactions as customdata.
               # This can be specified for each col and must  have
               # the same length as the DataFrame being passed in.
               dict_customdata={},
               # -----------------------------------------------------------
               # x-axis options
               xtitle='',
               xnticks=10,
               xrange=None,
               # Option to specify x-axis type, valid options are
               # - (default, auto), linear, log, date, category, multicategory.
               xtype='-',
               xfontsize=20,
               xangle=0,
               xhoverformat=None,
               xtickformat=None,
               reverse_x=False,
               add_xmargins=True,
               # -----------------------------------------------------------
               # y-axis options
               ytitle=None,
               ynticks=10,
               yrange=None,
               yfontsize=20,
               yangle=0,
               logy=False,
               # right y-axis options
               rytitle=None,
               ryrange=None,
               rlogy=False,
               # -----------------------------------------------------------
               # horizontal/vertical lines/rects
               hlines=[],
               vlines=[],
               hrects=[],
               vrects=[],
               # -----------------------------------------------------------
               # hover options
               hover_prec=1,
               # -----------------------------------------------------------
               # spike (crosshair) options
               crosshair=False,
               # -----------------------------------------------------------
               # figure options
               width=1500,
               height=800,
               margin_left=80,
               margin_right=60,
               margin_top=50,
               margin_bottom=100,
               range_buttons=False,
               range_slider=False,
               debug=False):
    '''
    Create a fig object from a DataFrame that is a line + stacked bars/grouped bars/area charts.
    By default the 0th column will be a line and all other columns
    will be stacked bars.

    To change the columns that are lines, specify as a list of positions like
    linecols=[0, 5]
    in which case the 0th and 5th columns will become lines.
    Can also specify
    linecolors=['GDP', 'inflation']
    in which these columns will become lines.
    '''

    if debug:
        print('-' * 20)
        print('start of create_fig with df:')
        print(df[-10:])
        print('linecols = ' + str(linecols))
        print('rlinecols = ' + str(rlinecols))

    # Check hover_prec can be interpreted as int
    try:
        hover_prec = int(hover_prec)
        # Convert to str
        hover_prec = str(hover_prec)
    except (TypeError, ValueError):
        print('add_segment(): hover_prec must be interpretable as int')
        sys.exit(-1)

    # Create line chart for line_cols
    fig = add_lines(df,
                    linecols=linecols, rlinecols=rlinecols,
                    dict_colors=dict_colors,
                    dict_markers=dict_markers,
                    dict_legends=dict_legends,
                    dict_hover=dict_hover,
                    dict_customdata=dict_customdata,
                    right_yaxis=bar_right,
                    hover_prec=hover_prec)

    # Adjust margins
    fig.update_layout(margin=dict(l=margin_left, r=margin_right, t=margin_top, b=margin_bottom))

    # Parse input linecols and rlinecols
    line_cols = _parse_cols(linecols, df)
    rline_cols = _parse_cols(rlinecols, df)

    # Parse specified barcols.
    bar_cols = _parse_cols(barcols, df)

    if debug:
        print('-' * 20)
        print('line_cols:')
        print('\n'.join(line_cols))
        
        print('-' * 20)
        print('rline_cols:')
        print('\n'.join(rline_cols))
        
        print('-' * 20)
        print('bar_cols:')
        print('\n'.join(bar_cols))

    # Add stacked bars
    if not area:
        fig = add_bars(df, bar_cols,
                       fig=fig,
                       dict_colors=dict_colors,
                       dict_patterns=dict_patterns,
                       dict_legends=dict_legends,
                       dict_hover=dict_hover,
                       dict_customdata=dict_customdata,
                       list_barcolors=list_barcolors,
                       barwidth=barwidth,
                       stack=stack, bar_right=bar_right, opacity=bar_opacity,
                       hover_prec=hover_prec,
                       legendrank_offset=len(line_cols))
    else:
        fig = add_area(df, bar_cols,
                       fig=fig,
                       dict_colors=dict_colors,
                       # Not available as of plotly 5.1.0
                       # dict_patterns=dict_patterns,
                       dict_legends=dict_legends,
                       dict_hover=dict_hover,
                       dict_customdata=dict_customdata,
                       bar_right=bar_right, opacity=bar_opacity,
                       hover_prec=hover_prec,
                       legendrank_offset=len(line_cols))

    # Set width, height of fig
    fig.update_layout(title=figtitle,
                      width=width, height=height,
                      dragmode='pan'
    )

    if xtype != '-':
        fig.update_xaxes(type=xtype)
        
    if xtype not in ['-', 'date']:
        # Also turn off range_buttons
        range_buttons = False

    xrange = _parse_xrange(xrange, df, add_margins=add_xmargins)

    fig = _update_xaxes(fig, title=xtitle,
                        xrange=xrange,
                        xnticks=xnticks,
                        xangle=xangle,
                        xfontsize=xfontsize,
                        xtickformat=xtickformat,
                        xtype=xtype,
                        reverse_x=reverse_x)
        
    # Set y-axis range
    yrange = _parse_yrange(yrange, df)
    fig = _update_yaxes(fig, title=ytitle,
                        yrange=yrange,
                        ynticks=ynticks,
                        yangle=yangle,
                        yfontsize=yfontsize,
                        logy=logy,
                        secondary_y=False)

    # Set right y-axis range.
    # If rlinecols is None and bar_right is False,
    # apply the same as left y-axis
    if rlinecols is None and bar_right == False:
        fig = _update_yaxes(fig, title=ytitle,
                            yrange=yrange,
                            ynticks=ynticks,
                            yangle=yangle,
                            yfontsize=yfontsize,
                            logy=logy,
                            secondary_y=True)
    # Otherwise use the variables
    # ryrange, rytitle, rlogy
    else:
        yrange = _parse_yrange(ryrange, df)
        fig = _update_yaxes(fig, title=rytitle,
                            yrange=ryrange,
                            ynticks=ynticks,
                            yangle=yangle,
                            yfontsize=yfontsize,
                            logy=rlogy,
                            secondary_y=True)

    # Add fill if specified
    if fillcols is not None:
        try:
            lo, hi = fillcols
        except TypeError:
            print('create_fig(): Cannot split fillcols into lo, hi')
            print('fillcols:')
            print(fillcols)
            sys.exit(-1)
        # Call add_fill()
        if fillcolors is None:
            # Use default colors
            fig = add_fill(df, lo, hi,
                           fig=fig,
                           right_yaxis=fillright)
        else:
            fig = add_fill(df, lo, hi,
                           fig=fig,
                           right_yaxis=fillright,
                           colors=fillcolors)
    
    # Add hlines, vlines, hrects, vrects
    for _hline in hlines:
        fig = add_hline(fig, _hline)
    for _vline in vlines:
        fig = add_vline(fig, _vline)
    for _hrect in hrects:
        fig = add_hrect(fig, _hrect)
    for _vrect in vrects:
        fig = add_vrect(fig, _vrect)
    
    # Set legend
    if showlegend:
        fig.update_layout(legend={'xanchor' : "left",
                                  'yanchor' : "bottom",
                                  'x'       : 0.02,
                                  'y'       : 1.02,
                                  'orientation' : 'h',
                                  'bgcolor' : 'white',
                                  'bordercolor' : 'white',
                                  'borderwidth' : 2,
                                  # Set to "normal" for create_fig()
                                  'traceorder'  :'normal',
                                  'font' : {# 'family' : 'Courier',
                                      'size'   : 16,
                                      'color'   : 'black'}
                                  },
                          legend_title_text=legend_title
        )
    else:
        fig.update_layout(showlegend=False)

    fig = _update_hover(fig)

    if range_buttons:
        fig = _add_range_buttons(fig, xrange=xrange)
    if range_slider:
        fig = _add_range_slider(fig, xrange=xrange)

    # Adjust xhoverformat
    if xhoverformat is not None:
        fig.update_traces(xhoverformat=xhoverformat)
        
    # Add crosshair (spike) if specified
    if crosshair:
        fig.update_xaxes(showspikes=True, spikecolor="rgba(50,50,50,0.7)",
                         spikethickness=1, spikesnap="cursor", spikemode="across", spikedash='dash')
        fig.update_yaxes(showspikes=True, spikecolor="rgba(50,50,50,0.7)",
                         spikethickness=1, spikesnap="cursor", spikemode="across", spikedash='dash')
        fig.update_layout(spikedistance=1000, hoverdistance=100)

    return fig

def create_heatmap(df,
                   figtitle='',
                   legend_title='',
                   # -----------------------------------------------------------
                   # x-axis options
                   xtitle=None,
                   xfontsize=20,
                   xangle=0,
                   xtickformat=None,
                   # -----------------------------------------------------------
                   # y-axis options
                   ytitle=None,
                   yfontsize=20,
                   yangle=0,
                   # -----------------------------------------------------------
                   # heatmap options
                   # See https://plotly.com/python/builtin-colorscales/
                   # for available built-in color scales.
                   colortitle='',
                   colorscale='Rainbow',
                   show_text=True,
                   # -----------------------------------------------------------
                   # figure options
                   width=1500,
                   height=800,
                   margin_left=80,
                   margin_right=60,
                   margin_top=50,
                   margin_bottom=100,
                   debug=False):
    '''
    Create a fig object from a DataFrame that is a heatmap.
    The columns will be shown on the x-axis, and the index will be shown on the y-axis.
    '''

    if debug:
        print('-' * 20)
        print('start of create_heatmap with df:')
        print(df[-10:])

    # Create line chart for line_cols
    fig = go.Figure(data=go.Heatmap(z=df,
                                    x=df.columns, y=df.index,
                                    colorscale=colorscale,
                                    hoverongaps=False,
                                    # need option for colortitle
                                    text = df.values.astype(str))
    )
    fig.update_xaxes(type='category')
                                    
    # Set width, height of fig
    fig.update_layout(title=figtitle,
                      width=width, height=height,
                      dragmode='pan'
    )

    # Adjust margins
    fig.update_layout(margin=dict(l=margin_left, r=margin_right, t=margin_top, b=margin_bottom))

    # Set x, y titles
    fig = _update_xaxes(fig, title=xtitle,
                        xtype='category', xnticks=len(df.columns),
                        xangle=xangle, xfontsize=xfontsize,
                        xtickformat=xtickformat)
    fig = _update_yaxes(fig, title=ytitle,
                        ynticks=len(df),
                        yangle=yangle, yfontsize=yfontsize,
                        # Not specifying these for heatmap causes error.
                        row=None, col=None)

    # Set legend
    fig.update_layout(legend={'xanchor' : "left",
                              'yanchor' : "bottom",
                              'x'       : 0.02,
                              'y'       : 1.02,
                              'orientation' : 'h',
                              'bgcolor' : 'white',
                              'bordercolor' : 'white',
                              'borderwidth' : 2,
                              # Set to "normal" for create_heatmap()
                              'traceorder'  :'normal',
                              'font' : {# 'family' : 'Courier',
                                        'size'   : 16,
                                        'color'   : 'black'}
                              },
                      legend_title_text=legend_title
    )

    fig = _update_hover(fig)

    return fig

def add_hline(fig, hlineobj):
    '''
    Add horizontal line to existing fig using class HLine object.
    '''

    # Check fig is not None
    if fig is None:
        print('fig was None')
        sys.exit(-1)

    # Add hline
    fig.add_hline(y=hlineobj.y,
                  line_width=hlineobj.line_width,
                  line_dash=hlineobj.line_dash,
                  line_color=hlineobj.line_color,
                  opacity=hlineobj.opacity,
                  annotation_text=hlineobj.text,
                  annotation_position=hlineobj.position,
                  annotation = {'font_size'   : hlineobj.font_size,
                                'font_color'  : hlineobj.font_color,
                                'opacity'     : hlineobj.font_opacity,
                                'font_family' : hlineobj.font_family},
                  row=hlineobj.row, col=hlineobj.col,
                  secondary_y=hlineobj.secondary_y)
    
    return fig

def add_vline(fig, vlineobj):
    '''
    Add vertical line to existing fig using a VLine object.
    '''

    # Check fig is not None
    if fig is None:
        print('fig was None')
        sys.exit(-1)

    # Try to onvert str(vlineobj.x) into valid time, then need to convert to
    # timestamp in milliseconds, otherwise text will give error.
    # See https://github.com/plotly/plotly.py/issues/3065
    try:
        # The conversion to str prevents floats like 3
        # to be interpreted as a time of 1970-01-01 00:00:00
        # with the nanosecond part being 3.
        x = pd.Timestamp(str(vlineobj.x))
        # convert to milliseconds
        x = x.timestamp() * 1000
    except ValueError:
        # Try to convert as float
        try:
            x = float(str(vlineobj.x))
        except ValueError:
            print('Could not convert ' + str(vlineobj.x) + ' into pd.Timestamp or float')
            sys.exit(-1)
            
    # Add vline
    fig.add_vline(x=x,
                  line_width=vlineobj.line_width,
                  line_dash=vlineobj.line_dash,
                  line_color=vlineobj.line_color,
                  opacity=vlineobj.opacity,
                  annotation_text=vlineobj.text,
                  annotation_position=vlineobj.position,
                  annotation = {'font_size'   : vlineobj.font_size,
                                'font_color'  : vlineobj.font_color,
                                'opacity'     : vlineobj.font_opacity,
                                'font_family' : vlineobj.font_family},
                  row=vlineobj.row, col=vlineobj.col,
                  secondary_y=vlineobj.secondary_y)
    
    return fig

def add_hrect(fig, hrectobj):
    '''
    Add horizontal rectangle to existing fig using HRect object
    '''

    # Check fig is not None
    if fig is None:
        print('fig was None')
        sys.exit(-1)

    # Add hrect
    fig.add_hrect(y0=hrectobj.y0,
                  y1=hrectobj.y1,
                  line_width=hrectobj.line_width,
                  line_dash=hrectobj.line_dash,
                  line_color=hrectobj.line_color,
                  fillcolor=hrectobj.fill_color,
                  opacity=hrectobj.opacity,
                  annotation_text=hrectobj.text,
                  annotation_position=hrectobj.position,
                  annotation = {'font_size'   : hrectobj.font_size,
                                'font_color'  : hrectobj.font_color,
                                'opacity'     : hrectobj.font_opacity,
                                'font_family' : hrectobj.font_family},
                  row=hrectobj.row, col=hrectobj.col,
                  secondary_y=hrectobj.secondary_y)
    return fig

def add_vrect(fig, vrectobj):
    '''
    Add vertical rectangle to existing fig using vrect object.
    Useful for shading periods for recession etc.
    '''

    # Check fig is not None
    if fig is None:
        print('fig was None')
        sys.exit(-1)

    # Try to onvert str(vrectobj.x0) into valid time, then need to convert to
    # timestamp in milliseconds, otherwise text will give error.
    # See https://github.com/plotly/plotly.py/issues/3065
    try:
        # The conversion to str prevents floats like 3
        # to be interpreted as a time of 1970-01-01 00:00:00
        # with the nanosecond part being 3.
        x0 = pd.Timestamp(str(vrectobj.x0))
        x1 = pd.Timestamp(str(vrectobj.x1))
        # convert to millisecond
        x0 = x0.timestamp() * 1000
        x1 = x1.timestamp() * 1000
    except ValueError:
        # Try to convert as float
        try:
            x0 = float(str(vrectobj.x0))
            x1 = float(str(vrectobj.x1))
        except ValueError:
            print('Could not convert ' + str(vrectobj.x0) + ' and ' + str(vrectobj.x1) + ' into pd.Timestamp or float')
            sys.exit(-1)
        
    # Add vrect
    fig.add_vrect(x0=x0,
                  x1=x1,
                  line_width=vrectobj.line_width,
                  line_dash=vrectobj.line_dash,
                  line_color=vrectobj.line_color,
                  fillcolor=vrectobj.fill_color,
                  opacity =vrectobj.opacity,
                  annotation_text=vrectobj.text,
                  annotation_position=vrectobj.position,
                  annotation = {'font_size'   : vrectobj.font_size,
                                'font_color'  : vrectobj.font_color,
                                'opacity'     : vrectobj.font_opacity,
                                'font_family' : vrectobj.font_family},
                  row=vrectobj.row, col=vrectobj.col,
                  secondary_y=vrectobj.secondary_y)
    
    return fig
