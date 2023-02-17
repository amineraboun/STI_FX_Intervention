'''
Library to use Bokeh for interactive visualizations.
Mostly for the purpose of using Bokeh tables,
which are sortable and thus more useful than plotly tables.
'''

import os
import sys

import numpy as np
from pandas.api.types import is_numeric_dtype, is_bool_dtype

import bokeh
bokeh_version = bokeh.__version__
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, HTMLTemplateFormatter
from bokeh.embed import components

def _gen_format_template(thresh=0, thresh_sign='<',
                         prec=2,
                         cell_font_size=20,
                         thresh_color='red', thresh_bg_color='',
                         non_thresh_color='', non_thresh_bg_color='',
                         nan_color='grey', nan_bg_color='',
                         nan_val='---'):
    '''
    Returns a template str with formatting based on threshold and decimal precision.
    To specify no threshold, set thresh to None (False will be interpreted as 0).
    For non-numerical columns, both thresh = None and prec = None should be specified.

    The expression to be evaluated is
    `value` `thresh_sign` `thresh`
    so if thresh_sign = "<" and thresh = 0, the evaluation is
    `value < 0
    and all values below 0 will be shown with text in thresh_color
    and background cell as thresh_bg_color.

    The options non_thresh_color and non_thresh_bg_color will color
    the text and background for values that do *not* meet the above evaluation.

    If there are any NA values, these are given text and background color of
    nan_color and nan_bg_color.
    '''

    if prec is None:
        val = """<%= (value) %>"""
    else:
        # val = """<%= (value).toFixed(""" + str(prec) + """) %>"""
        val = """<%= (function decidenan(){
                if(isNaN(value) === true){
                    return( '""" + nan_val + """' )
                } else{
                    return( (value).toFixed(""" + str(prec) + """) )
                }
        }()) %>"""

    # If no threshold 
    if thresh is None:
        template = """
        <div style="font-size: """ + str(cell_font_size) + """px;">""" + val + """</div>"""
    else:
        template = """
        <div style="background:<%= 
            (function colorfromfloat(){
                if(isNaN(value)){
                    return('""" + nan_bg_color + """')
                }
                else if(value """ + thresh_sign + ' ' + str(thresh) + """){
                    return('""" + thresh_bg_color + """')}
                else{
                    return('""" + non_thresh_bg_color + """')}
                }()
            )%>;
            color: <%= 
            (function colorfromint(){
                if(isNaN(value)){
                    return('""" + nan_color + """')
                }
                else if(value""" + thresh_sign + ' ' + str(thresh) + """){
                    return('""" + thresh_color + """')}
                else{
                    return('""" + non_thresh_color + """')}
                }()
            )%>;
            font-size: """ + str(cell_font_size) + """px;
        ">""" + val + """</div>"""

    return template

def create_bokeh_table(df,
                       # --------------------------------------
                       # Table size, options
                       height='auto',
                       width='auto',
                       sortable=True,
                       # --------------------------------------
                       # Whether index is a date and how to format
                       dateindex=True, dateformat='%Y-%m-%d',
                       # Specify True to ignore dateformat and use
                       # pandas formatting of PeriodIndex
                       periods=False,
                       # how many periods to show, set to None to show all.
                       # This will automatically be disabled for a non-date index.
                       nperiods = 20,
                       # If we want to rename index
                       indexname=None,
                       # --------------------------------------
                       # Colors of rows.
                       # TODO:
                       # This is set in CSS within template.html
                       # Check if this can be applied separately for different tables.
                       header_color='paleturquoise',
                       row_colors=['lavender', 'white'],
                       # --------------------------------------
                       # Decimal precision for numerical columns.
                       prec=1,
                       # Row heights
                       header_height=38,
                       row_height=25,
                       # --------------------------------------
                       # Column widths
                       index_width=250,
                       col_width=120,
                       # --------------------------------------
                       # Fonts
                       header_font_size=16,
                       header_font_color='black',
                       index_font_size=20,
                       index_font_color='grey',
                       cell_font_size=20,
                       cell_font_color='grey',
                       header_align='left',
                       cell_align='center',
                       # --------------------------------------
                       # Formatting for values below a certain threshold.
                       # If thresh is a float, apply to all numerical columns.
                       # If a dict between column names and threshold values is given,
                       # apply to each columns separately.
                       # Columns not specified will not have threshold applied.
                       # To turn off, set to None.
                       # Note that setting to False will be interpreted as 0.
                       thresh=0,
                       thresh_sign='<', # One of <, >, =
                       thresh_bg_color='',
                       thresh_color='red',
                       non_thresh_bg_color='',
                       non_thresh_color='',
                       # --------------------------------------
                       # Formatting for NA values
                       nan_val='---',
                       nan_color='grey', nan_bg_color=''):
    '''
    Create table using DataFrame in datatools format,
    where index is DatetimeIndex with all columns
    representing one variable.

    Returns <script> and <div> tags as strs,
    these can then be embedded into an HTML file.

    Default parameters from
    https://docs.bokeh.org/en/latest/docs/reference/models/widgets.tables.html#bokeh.models.widgets.tables.DataTable
    "align": "start",
    "aspect_ratio": null,
    "auto_edit": false,
    "autosize_mode": "force_fit",
    "background": null,
    "columns": [],
    "css_classes": [],
    "default_size": 300,
    "disabled": false,
    "editable": false,
    "fit_columns": null,
    "frozen_columns": null,
    "frozen_rows": null,
    "header_row": true,
    "height": 400,
    "height_policy": "auto",
    "index_header": "#",
    "index_position": 0,
    "index_width": 40,
    "js_event_callbacks": {},
    "js_property_callbacks": {},
    "margin": [5,5,5,5],
    "max_height": null,
    "max_width": null,
    "min_height": null,
    "min_width": null,
    "name": null,
    "orientation": "horizontal",
    "reorderable": true,
    "row_height": 25,
    "scroll_to_selection": true,
    "selectable": true,
    "sizing_mode": null,
    "sortable": true,
    "subscribed_events": [],
    "syncable": true,
    "tags": [],
    "visible": true,
    "width": 600,
    "width_policy": "auto"
    }    
    '''

    # Make copy of original so it is not affected
    _df = df.copy()

    # Format index
    if dateindex:
        # Cut off to most recent nperiods.
        if type(nperiods) == int:
            _df = _df[-nperiods:]
        elif nperiods is None:
            pass
        else:
            print('nperiods given as ' + str(type(nperiods)))
            print('Must be int or None')
            sys.exit(-1)

        # Format so that col "dates" is added and latest values are at top.
        if periods:
            # Convert to PeriodIndex and convert to str
            try:
                _df.index = _df.index.to_period().astype(str)
            except Exception as e:
                print('Could not convert index to PeriodIndex with exception ' + str(e))
                print(_df)
                sys.exit(-1)
        else:
            # Use specified date formatting
            _df.index = _df.index.strftime(dateformat)

        # Sort the index only if dateindex
        _df.sort_index(ascending=False, inplace=True)

    # Get the index name.
    # If it was not set, the below _df.sort_index(...).reset_index()
    # will set the column to be "index"
    indexcol = _df.index.name
    if indexcol is None:
        indexcol = 'index'

    # Rename indexcol if specified
    if indexname is not None:
        # Make sure the specified indexname is not a column.
        if indexname in _df.columns:
            print('Cannot specify ' + str(indexcol) + ' as indexname,')
            print('column with same name exists:')
            print(_df)
            sys.exit(-1)
        indexcol = indexname
        _df.index.name = indexcol

    # If the column is not numeric, replace NA with nan_val
    for col in _df.columns:
        if not is_numeric_dtype(_df[col]):
            _df[col] = _df[col].replace(np.nan, nan_val)

    # Create source of data,
    # which is a dict with keys for indexcol and columns
    # with a corresponding list of values for each.
    # There is no ambiguity in the order of the columns,
    # as DataTable() takes in an argument columns.
    source = ColumnDataSource(_df.reset_index().to_dict(orient='list'))

    # For index use simple 
    indextemplate = """
    <div style="font-size: """ + str(index_font_size) + """px;color:""" + index_font_color + """;">
    <%=value%>
    </div>
    """
    indexformatter =  HTMLTemplateFormatter(template=indextemplate)
    
    # Create list of TableColumns and add index.
    columns = [TableColumn(field=indexcol, title=indexcol,
                           formatter=indexformatter,
                           width=index_width)]

    # Template for numeric values
    for col in _df.columns:
        # Boolean types.
        #is_numeric_dtype below returns True, but table will be empty for bool cols
        # with numeric formatting below, so treat separately.
        if is_bool_dtype(_df[col]):
            template = _gen_format_template(thresh=None, prec=None,
                                            cell_font_size=cell_font_size)
        # Numeric types
        elif is_numeric_dtype(_df[col]):
            if thresh is None:
                _thresh = thresh
            else:
                # If a numerical value is provided, apply to all columns.
                try:
                    _thresh = float(thresh)
                except ValueError:
                    if type(thresh) == dict:
                        if col in thresh:
                            _thresh = thresh[col]
                            try:
                                _thresh = float(_thresh)
                            except ValueError:
                                print('If a dict is used for thresh, values must be numerical.')
                                print('Given thresh:')
                                print(thresh)
                                sys.exit(-1)
                        # If the column is not in the dict thresh, don't apply threshold
                        else:
                            _thresh = None
                    else:
                        print('thresh must be one of True, False, None or a dict')
                        print('between column names of df and values.')
                        print('Given thresh:')
                        print(thresh)
                        sys.exit(-1)

            template = _gen_format_template(thresh=_thresh, thresh_sign=thresh_sign,
                                            prec=prec,
                                            cell_font_size=cell_font_size,
                                            thresh_color=thresh_color, thresh_bg_color=thresh_bg_color,
                                            non_thresh_color=non_thresh_color, non_thresh_bg_color=non_thresh_bg_color,
                                            nan_color=nan_color, nan_bg_color=nan_bg_color,
                                            nan_val=nan_val)
        # Not boolean or numeric (text)
        else:
            template = _gen_format_template(thresh=None, prec=None,
                                            cell_font_size=cell_font_size)
        formatter =  HTMLTemplateFormatter(template=template)
        columns.append(TableColumn(field=col, title=col, formatter=formatter, width=col_width))

    # Fix height if specified
    if height == 'auto':
        # Automatically adjust to table's height
        height = row_height * len(_df) + header_height + 5
    else:
        # Otherwise just pass the value.
        pass

    if width == 'auto':
        width = index_width + len(_df.columns) * col_width
    else:
        pass

    # Create table
    data_table = DataTable(source=source, columns=columns,
                           sortable=sortable,
                           # don't show meaningless index
                           index_position=None,
                           # background='black',
                           row_height=row_height,
                           width=width, height=height)
    
    # This creates components of standalone documents.
    # script contains the data, div displays the plot.
    script, div = components(data_table)

    return script, div

def generate_html(outfilename, scripts, divs,
                  show=True):
    '''
    Generate an output HTML file from a list of scripts and divs.

    If show is True, the HTML file will open in a browser.
    '''

    # Read in template HTML file
    templatefilename = 'template_bokeh.html'
    if not os.path.isfile(templatefilename):
        print('File ' + templatefilename + ' does not exist')
        sys.exit(-1)
        
    with open(templatefilename) as infile:
        htmlfile = infile.read()

    # Replace BOKEH_VERSION with version used
    htmlfile = htmlfile.replace('BOKEH_VERSION', bokeh_version)

    # This assume sthe scripts and divs were properly
    # put together as lists.
    # Check that lengths are same
    if len(scripts) != len(divs):
        print('Length of scripts = ' + str(len(scripts)) + ', length of divs = ' + str(len(divs)))
        sys.exit(-1)
    nscripts = len(scripts)
    for iscript, (script, div) in enumerate(zip(scripts, divs)):
        if iscript != nscripts - 1:
            output_script = script + '\nBOKEH_SCRIPT'
            output_div    = div + '\nBOKEH_DIV'
        else:
            output_script = script
            output_div    = div
        # Replace BOKEH_SCRIPT, BOKEH_DIV with contents of script, div
        htmlfile = htmlfile.replace('BOKEH_SCRIPT', output_script)
        htmlfile = htmlfile.replace('BOKEH_DIV', output_div)
    
    # Save output
    with open(outfilename, 'w') as outfile:
        outfile.write(htmlfile)
        
    # Open HTML if show is True
    if show:
        import webbrowser
        webbrowser.open(outfilename, new=2)
