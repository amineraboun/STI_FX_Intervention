import os
import sys

import pandas as pd

# Set plotly template
import plotly.io as pio
# pio.templates shows available templates
# 'ggplot2', 'seaborn', 'simple_white', 'plotly',
# 'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
# 'ygridoff', 'gridon', 'none'
# Set template
template = 'presentation' # plotly_dark # plotly_white
pio.templates.default = template

# Set config
config = {'scrollZoom'    : True,  # allow scroll wheel
          'displayModeBar': True,  # always show mode bar
          'toImageButtonOptions': {
              'format': 'png', # one of png, svg, jpeg, webp
              'filename': 'custom_image',
              'width': 700,
              'height': 500,
              'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
          },
          'modeBarButtonsToAdd':['drawcircle', 'drawrect'],
}


from .plotly_utilities import create_table, create_fig_2col, create_fig, create_heatmap, add_lines, add_bars, add_area, add_fill, add_text, add_segment, \
    add_hline, add_vline, add_hrect, add_vrect
from .plotly_objects import HLine, VLine, HRect, VRect, Space, Heading, Heading1, Heading2, Heading3, NewPage, Markdown, Image

from .bokeh_utilities import bokeh_version
from .bokeh_utilities import create_bokeh_table

def read_csv_data(infilename):
    '''
    Read in csv file that was created from datatools.
    '''
    if not os.path.isfile(infilename):
        print('File ' + infilename + ' does not exist')
        sys.exit(-1)
    df = pd.read_csv(infilename, index_col=0, parse_dates=[0])

    # Drop any periods that do not have any data
    df.dropna(axis=0, how='all', inplace=True)

    return df

def create_html(outfilename, objects=[],
                # title is used for both <head><title> and <h1> at top
                title='',
                datafilename=None,
                show=True,
                # dict between link text and URL
                links={},
                debug=False,
                *args, **kwargs):
    '''
    Create output HTML file.
    '''

    if debug:
        print('Start of create_html with:')
        print('outfilename = ' + str(outfilename))
        print('objects has ' + str(len(objects)) + ' elements')

    # Read in template HTML file,
    # this file is in the same folder as this file.
    templatefilename = os.path.dirname(os.path.abspath(__file__)) + '/template.html'
    if not os.path.isfile(templatefilename):
        print('File ' + templatefilename + ' does not exist')
        sys.exit(-1)
        
    with open(templatefilename) as infile:
        htmltext = infile.read()

    # Replace BOKEH_VERSION with version used
    htmltext = htmltext.replace('BOKEH_VERSION', bokeh_version)

    # Replace background color
    # Background color of each template can be found with
    # pio.templates['plotly_dark']['layout']['paper_bgcolor']
    bgcolor_rgb = pio.templates[pio.templates.default]['layout']['paper_bgcolor']
    # Convert this to hex
    if bgcolor_rgb == 'white':
        bgcolor_hex = '#FFFFFF'
    elif bgcolor_rgb is None:
        bgcolor_hex = '#FFFFFF'
    elif bgcolor_rgb.find('rgb') != -1:
        bgcolor_hex = rgbstr_to_hexstr(bgcolor_rgb)
    else:
        print('Cannot convert ' + bgcolor_rgb + ' to hex value')
        sys.exit(-1)
    htmltext = htmltext.replace('BGCOLOR_HEX', bgcolor_hex)

    # Replace TITLE
    htmltext = htmltext.replace('TITLE', title)

    # Get output dir
    outdir = os.path.dirname(os.path.abspath(outfilename))
    basename = os.path.basename(outfilename)
    imagedir = os.path.abspath(outdir + '/__' + basename + '__images__')

    # Process each object that was passed in
    for obj in objects:
        # If obj was a Space, Heading, Markdown, Image object
        if isinstance(obj, Space) or isinstance(obj, Heading) or isinstance(obj, Markdown) or isinstance(obj, Image):
            if not isinstance(obj, Image):
                htmltext += '\n  ' + obj.to_html()
            else:
                htmltext += '\n  ' + obj.to_html(outdir=imagedir)
            
        # If obj was a tuple of script, div
        # coming from Bokeh table
        elif type(obj) == tuple and len(obj) == 2:
            script, div = obj
            # Replace BOKEH_SCRIPT with the script
            htmltext = htmltext.replace('BOKEH_SCRIPT', script + '\n    BOKEH_SCRIPT')

            # Add in div
            htmltext += '\n    ' + div
            
        # Otherwise this is a plotly fig object which we can convert to HTML
        else:
            htmltext += '\n  ' + obj.to_html(full_html=False,
                                             include_plotlyjs='cdn',
                                             config=config)
        if debug:
            print('-' * 20)
            print('added new object')
    # end of loop over objects

    # Remove BOKEH_SCRIPT, BOKEH_DIV from file
    htmltext = htmltext.replace('BOKEH_SCRIPT', '')
    htmltext = htmltext.replace('BOKEH_DIV', '')
    
    # Data download link
    if datafilename:
        datalink = '''\n    <div align="center"><p style="font-size:24px;"><a href="''' + datafilename + '''" type="text/csv">Download data</a></p></div>'''
        htmltext = htmltext + datalink

    # Create links to other pages
    for text in links:
        url = links[text]
        linktext = '''\n    <div align="center"><p style="font-size:24px;"><a href="''' + url + '''">''' + text + '''</a></p></div>'''
        htmltext = htmltext + linktext
        
    tail = '''\n  </body>\n</html>'''
    htmltext = htmltext + tail

    # Write out file
    try:
        with open(outfilename, 'w') as outfile:
            outfile.write(htmltext)
    except Exception as e:
        print('Writing out file ' + outfilename + ' failed with error:')
        print(e)
        sys.exit(-1)

    if debug:
        print('-' * 20)
        print('wrote out file')

    if show:
        # Show output HTML
        import webbrowser
        webbrowser.open('file://' + os.path.abspath(outfilename), new=2)
