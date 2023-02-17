'''
2021-11-06 Kei Moriya

Test of Bokeh tables.

Combined from
https://docs.bokeh.org/en/latest/docs/user_guide/interaction/widgets.html#datatable
https://stackoverflow.com/questions/42740477/bokeh-datatable-with-conditionally-coloured-cells/42742954#42742954
'''

import numpy as np
import pandas as pd

import bokeh
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, HTMLTemplateFormatter
from bokeh.embed import components # file_html
# from bokeh.io import show, save
# from bokeh.resources import CDN

from imf_datatools import get_haver_data

dict_cols = {'PGDPH@USECON' : 'GDP',
             'PTCH@USECON' : 'C',
             'PTGH@USECON' : 'G',
             'PTFH@USECON' : 'I',
             'PTVH@USECON' : 'Inventories',
             'PTXH@USECON' : 'X',
             'PTMH@USECON' : 'M'}

df = get_haver_data(list(dict_cols.keys()))
# This is a dict with keys 'dates' and column names,
# with corresponding list of values.
# So there is no ambiguity in the order of the column values.
# The ambiguity of 'dates' and columns is taken care of with
# the list `columns`.
df.index = df.index.strftime('%Y-%m-%d (%a)')
source = ColumnDataSource(df.sort_index(ascending=False).reset_index().to_dict(orient='list'))

def gen_number_format_template(thresh=0, decimals=2):
    '''
    Returns a template str with formatting based on threshold and decimals.
    '''
    return """
    <div style="background:<%= 
        (function colorfromfloat(){
            if(value < """ + str(thresh) + """){
                return("pink")}
            else{
                return("turquoise")}
            }()
        )%>;
        color: <%= 
        (function colorfromint(){
            if(value < """ + str(thresh) + """){
                return('yellow')}
            else{
                return('black')}
            }()
        )%>;
        font-size: 20px;
    ">
      <%= (value).toFixed(""" + str(decimals) + """) %>
    </div>
    """

formatter =  HTMLTemplateFormatter(template=gen_number_format_template())

dateformatter = DateFormatter(format='%Y-%m-%d (%a)',
                              text_color='red')
datestrformatter = """
<div style="font-size: 20px;color:green;">
  <%=value%>
</div>
    """
datestrformatter =  HTMLTemplateFormatter(template=datestrformatter)

# Create list of TableColumns
columns = [TableColumn(field="dates", title="Date",
                       # formatter=dateformatter
                       formatter=datestrformatter,
                       width=450)]
for col in df.columns:
    columns.append(TableColumn(field=col, title=dict_cols[col], formatter=formatter))
    
data_table = DataTable(source=source, columns=columns,
                       # don't show meaningless index
                       index_position=None,
                       # background='black',
                       row_height=30,
                       width=450 + len(df.columns) * 100, height=800)

# Create text of HTML file
# html = file_html(data_table, CDN, 'my plot')

# This will show the widget in a browser window
# show(data_table)

# This will save the file
# save(data_table, 'data_table.html', title='my plot')

# This creates components of standalone documents.
# script contains the data, div displays the plot.
script, div = components(data_table)

# Read in template HTML file
with open('bokeh_table_template.html') as infile:
    htmlfile = infile.read()

# Replace BOKEH_VERSION with version used
bokeh_version = bokeh.__version__
htmlfile = htmlfile.replace('BOKEH_VERSION', bokeh_version)

# Replace BOKEH_SCRIPT with contents of script
htmlfile = htmlfile.replace('BOKEH_SCRIPT', script)

# Replace BOKEH_DIV with contents of div
htmlfile = htmlfile.replace('BOKEH_DIV', div)

# Save output
outfilename = 'output.html'
with open(outfilename, 'w') as outfile:
    outfile.write(htmlfile)

# Open
import webbrowser
webbrowser.open(outfilename, new=2)
