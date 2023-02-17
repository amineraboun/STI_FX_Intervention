'''
2021-08-25 Kei Moriya

Example of line plot in Plotly.
'''

import os
import sys
import importlib

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.io as pio
# pio.templates shows available templates
# 'ggplot2', 'seaborn', 'simple_white', 'plotly',
# 'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
# 'ygridoff', 'gridon', 'none'

import plotly_utilities
importlib.reload(plotly_utilities)

# Set template
template = 'plotly_dark'
pio.templates.default = template

# Set config
config = {'scrollZoom': True,     # allow scroll wheel
          'displayModeBar': True, # always show mode bar
          'toImageButtonOptions': {
              'format': 'png', # one of png, svg, jpeg, webp
              'filename': 'custom_image',
              'width': 700,
              'height': 500,
              'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
          },
          'modeBarButtonsToAdd':['drawcircle', 'drawrect'],
}

outfilename = 'lines.html'

# Read in data
infilename = 'data/Aus_diffusion.csv'
# infilename = 'data/CostaRica_ext.csv'
# infilename = 'data/CostaRica_embi.csv'
if not os.path.isfile(infilename):
    print('File ' + infilename + ' does not exist')
    sys.exit(-1)
df = pd.read_csv(infilename, index_col=0, parse_dates=[0])

# Create Plotly chart of line chart
title = 'Australia Diffusion'
width = 1200
height = 600

# Line opacity
line_opacity = 0.7

# Parameters for hover
hover_bgcolor = 'white'
hover_font_size = 12
hover_font_color = 'black'
hover_font_family = 'Times Roman'

# Parameters for x-axis
xlog = False
xaxis_title = 'dates'
xaxis_title_font_size = 24
xaxis_title_font_color = 'blue'
xtickfont_size = 20
xtickfont_color = 'cyan'
xtickangle = 45

xrange = None # [pd.Timestamp('2010-01-01'), pd.Timestamp.today()]
yrange = None # [-2, 80]

# x-axis border line
xshowline = True
xlinewidth = 2
xlinecolor = 'fuchsia'
xmirror = True

# Ticks for x-axis
xtickpos = "inside"
xnticks = 20
xtickcolor = 'white'
xticklen = 10

# x-axis grid
xshowgrid = True
xgridwidth = 1
xgridcolor = 'LightPink'

# Spikes for x-axis
showspikes = True
spikecolor = "green"
spikesnap = "cursor"
spikemode = "across"
spikethickness = 2

# Parameters for y-axis
ylog = False
yaxis_title = 'Aus diffusion'
yaxis_title_font_size = 24
yaxis_title_font_color = 'red'
ytickfont_size = 20
ytickfont_color = 'crimson'
ytickangle = 45

# y-axis border line
yshowline = True
ylinewidth = 2
ylinecolor = 'aqua'
ymirror = True

# Ticks for y-axis
ytickpos = "inside"
ynticks = 20
ytickcolor = 'white'
yticklen = 10

# y-axis grid
yshowgrid = True
ygridwidth = 1
ygridcolor = 'LightPink'

# Zero line for y-axis
yzeroline = True
yzerolinecolor = 'white'
yzerolinewidth = 2

cols = df.columns
# Format hover values
# DOES NOT WORK!!!
hover_format_dict = {col : True for col in cols}
hover_format_dict = {':.3f' : [col for col in cols[:1]]}
# hover_format_dict = {'PMI' : False}
# hover_format_dict = {}

fig = px.line(df, x=df.index, y=cols,
              log_x=xlog,
              log_y=ylog,
              title=title,
              width=width,
              height=height,
              template=template,
              # Change formatting of hover values
              # hover_data=hover_format_dict,
              )

# Disable default hover template
# (gets rid of variable=, dates=, value= for each hover label)
fig.update_traces(hovertemplate=None)

# Show a single hover label for each x (date)
# fig.update_layout(hovermode='x unified')

# Show a single hover label together for each x (date)
fig.update_layout(hovermode='x unified')

# Customize hover text
fig.update_layout(hoverlabel={'bgcolor'     : hover_bgcolor,
                              'font_size'   : hover_font_size,
                              'font_color'   : hover_font_color,
                              'font_family' : hover_font_family})

# Customize markers
# (does not work for px.line)
fig.update_traces(marker=dict(size=12,
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))

# Opacity for lines
fig.update_traces(opacity=line_opacity,
                  selector={'mode' : 'lines'})

# Customize hover align
fig.update_layout(hoverlabel_align='right')

# Customize legend
# Parameters for legend
#legend_params = dict(legend_title = 'index',
#                     legend_bgcolor = None,
#                     legend_borderwidth = 1,
#                     legend_bordercolor = 'white',
#                     legend_title_font_size = 14,
#                     legend_font_size = 10,
#                     legend_xxx = 333,
#                     legend_yyy = 999,
#                     )
legend_params = dict()
plotly_utilities.update_legend(fig, **legend_params)

# Customize x-axis
fig.update_xaxes(title_text=xaxis_title,
                 title_font_size=xaxis_title_font_size,
                 title_font_color=xaxis_title_font_color,
                 tickfont_size=xtickfont_size,
                 tickangle=xtickangle,
                 # range
                 range=xrange,
                 # border line
                 showline=xshowline,
                 linewidth=xlinewidth,
                 linecolor=xlinecolor,
                 mirror=xmirror,
                 # grid
                 showgrid=xshowgrid,
                 gridwidth=xgridwidth,
                 gridcolor=xgridcolor,
                 # ticks
                 ticks=xtickpos,
                 nticks=xnticks,
                 tickcolor=xtickcolor,
                 ticklen=xticklen)

# Customize y-axis
fig.update_yaxes(title_text=yaxis_title,
                 title_font_size=yaxis_title_font_size,
                 title_font_color=yaxis_title_font_color,
                 tickfont_size=ytickfont_size,
                 tickangle=ytickangle,
                 # range
                 range=yrange,
                 # border line
                 showline=yshowline,
                 linewidth=ylinewidth,
                 linecolor=ylinecolor,
                 mirror=ymirror,
                 # grid
                 showgrid=yshowgrid,
                 gridwidth=ygridwidth,
                 gridcolor=ygridcolor,
                 # ticks
                 ticks=ytickpos,
                 nticks=ynticks,
                 tickcolor=ytickcolor,
                 ticklen=yticklen)

# Customize 0 on y-axis
fig.update_yaxes(zeroline=yzeroline,
                 zerolinecolor=yzerolinecolor,
                 zerolinewidth=yzerolinewidth)

# Spikes for x-axis
fig.update_xaxes(showspikes=showspikes, spikecolor=spikecolor, spikesnap=spikesnap, spikemode=spikemode, spikethickness=spikethickness)

fig.show(config=config)
fig.write_html(outfilename)
print('Created ' + outfilename + '...')

