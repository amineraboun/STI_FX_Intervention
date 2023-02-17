'''
2021-09-30 Kei Moriya

Create all HTML outputs and link together.

****************************************************************************
THIS FILE MUST BE PLACED OUTSIDE OF THE imfplotly DIR SO IT CAN BE IMPORTED.
****************************************************************************
'''

import os
import sys

import imfplotly

masterfilename = 'master.html'
backlink = {'Back to index' : masterfilename}
links = dict()

#--------------------------------------------------------------------
# Australia GDP
#--------------------------------------------------------------------
objects = []
infilename = 'data/Aus_GDP.csv'
df = imfplotly.read_csv_data(infilename)

# -----------------------------------------------------
# Create lines + stacked bars for GDP

title = imfplotly.Heading1('Australia GDP')
objects.append(title)
subtitle = imfplotly.Heading2('National Accounts')
objects.append(subtitle)

# Add Markdown
text = 'This is an example of **Markdown** with some <span style="color:red">red</span> text'
markdown = imfplotly.Markdown(text)
objects.append(markdown)

figtitle = 'Australia GDP by Components'
linecols = df.columns[0]
dict_colors = {df.columns[0] : {'color' : 'black',
                                'width' : 4,
                                'dash'  : None},
               df.columns[1] : {'color' : 'red'}
}
dict_patterns={df.columns[1] : {'shape' : '+', 'size' : 5, 'fgcolor' : 'blue', 'fgopacity' : 0.3, 'bgcolor' : 'red'}}

fig = imfplotly.create_fig(df,
                           linecols=linecols,
                           barcols=df.columns[1:],
                           dict_colors=dict_colors,
                           dict_patterns=dict_patterns,
                           figtitle=figtitle,
                           bar_opacity=0.7,
                           # barwidth=1000*3600*24*10, # 10 days
                           hover_prec=2,
                           xhoverformat='%Y-Q%q',
                           xtickformat='%YQ%q',
                           reverse_x=True,
                           showlegend=False,
                           xrange=30)
objects.append(fig)


#fig2 = imfplotly.create_fig(df,
#                            linecols=linecols,
#                            dict_colors=dict_colors,
#                            figtitle=figtitle,
#                            bar_opacity=0.7,
#                            # barwidth=1000*3600*24*10, # 10 days
#                            hover_prec=2,
#                            xhoverformat='%Y-Q%q',
#                            xrange=30)
#objects.append(fig)
#
#outfilename = 'out_line_bar.html'
#title = 'Nicaragua Remittances'
#imfplotly.create_html(outfilename, objects,
#                      title=title, datafilename=infilename,
#                      links=backlink,
#                      show=True)
#sys.exit(0)

# -----------------------------------------------------
# Create space in between
space = imfplotly.Space(0.5)
objects.append(space)

# -----------------------------------------------------
# Create table for GDP
table = imfplotly.create_bokeh_table(df, nperiods=30)
objects.append(table)

# -----------------------------------------------------
# Create output HTML file
outfilename = 'out_Aus_gdp.html'
title = 'Australia GDP'
imfplotly.create_html(outfilename, objects,
                      title=title, datafilename=infilename,
                      links=backlink,
                      show=False)
links[title] = outfilename

#--------------------------------------------------------------------
# Australia IP
#--------------------------------------------------------------------
objects = []
infilename = 'data/Aus_IP.csv'
df = imfplotly.read_csv_data(infilename)

# -----------------------------------------------------
# Create dual line chart
figtitle = 'Australia Industrial Production'
linecols = df.columns[0]
dict_colors = {df.columns[0] : {'color' : 'black',
                                'width' : 4,
                                'dash'  : None},
               df.columns[1] : {'color' : 'red'}
}
fig = imfplotly.create_fig(df,
                           linecols=['IP (yoy, %change)', 'Mining IP (yoy, %change)'],
                           figtitle=figtitle,
                           legend_title='Seasonally Adjusted',
                           dict_colors=dict_colors,
                           xrange=25)
# Fill between
fig = imfplotly.add_fill(df, df.columns[0], df.columns[1],
                         fig=fig)
objects.append(fig)

# -----------------------------------------------------
# Create table
table = imfplotly.create_table(df, nperiods=30)
objects.append(table)

# -----------------------------------------------------
# Create output HTML file
outfilename = 'out_Aus_ip.html'
title = 'Australia IP'
imfplotly.create_html(outfilename, objects,
                      title=title, datafilename=infilename,
                      links=backlink,
                      show=False)
links[title] = outfilename

#--------------------------------------------------------------------
# Australia Labor
#--------------------------------------------------------------------
objects = []
infilename = 'data/Aus_labor.csv'
df = imfplotly.read_csv_data(infilename)
dict_colors = {df.columns[0] : {'color' : 'red'}}

# -----------------------------------------------------
# Create dual line chart
figtitle = ['Unemployment Rate', 'Australia Labor Market']
linecols = df.columns[0]
linecolslist = [df.columns[0], None, df.columns[1], df.columns[2]]
dict_colors = {df.columns[0] : {'color' : 'black',
                                'width' : 4,
                                'dash'  : None},
               df.columns[1] : {'color' : 'red'}
}
dict_legends = {df.columns[0] : False}
fig = imfplotly.create_fig_2col(df,
                                dict_colors=dict_colors,
                                dict_legends=dict_legends,
                                linecolslist=linecolslist,
                                figtitle=figtitle,
                                # showlegend=False,
                                xrange=30,
                                reverse_x=[False, True],
                                #xtickformat='%Y %b')
                                )

objects.append(fig)

# -----------------------------------------------------
# Create table
table = imfplotly.create_table(df, nperiods=30)
objects.append(table)

# -----------------------------------------------------
# Create output HTML file
outfilename = 'out_labor.html'
title = 'Australia Labor Market'
imfplotly.create_html(outfilename, objects,
                      title=title, datafilename=infilename,
                      links=backlink,
                      show=False)
links[title] = outfilename

#--------------------------------------------------------------------
# Dominican Republic monetary
#--------------------------------------------------------------------
objects = []
infilename = 'data/DominicanRepublic_monetary.csv'
df = imfplotly.read_csv_data(infilename)
linecols = df.columns[0]

# -----------------------------------------------------
# Create area chart
figtitle = 'Dominican Republic Monetary Policy'
dict_colors={df.columns[0] : {'color' : 'black'}}
fig = imfplotly.create_fig(df,
                           linecols=linecols,
                           barcols=df.columns[1:],
                           figtitle=figtitle,
                           dict_colors=dict_colors,
                           # Set area to True to get area chart
                           area=True,
                           bar_opacity=1,
                           xrange=30)
objects.append(fig)

# -----------------------------------------------------
# Create table
table = imfplotly.create_table(df, nperiods=30)
objects.append(table)

# -----------------------------------------------------
# Create output HTML file
outfilename = 'out_DR_monetary.html'
title = 'Dominican Republic Monetary Policy'
imfplotly.create_html(outfilename, objects,
                      title=title, datafilename=infilename,
                      links=backlink,
                      show=False)
links[title] = outfilename

#--------------------------------------------------------------------
# Mexico Inflation
#--------------------------------------------------------------------
objects = []
infilename = 'data/Mexico_inflation.csv'
df = imfplotly.read_csv_data(infilename)
linecols = df.columns[0]

# -----------------------------------------------------
# Create 2-col chart
figtitle = ['Mexico CPI', 'CPI Forecasts']
dict_colors = {df.columns[0] : {'color' : 'red'},
               df.columns[1] : {'color' : 'blue'},
               df.columns[2] : {'color' : 'green'}}
linecolslist = [list(df.columns[0:2]), None, df.columns[2], df.columns[3]]
_hline = imfplotly.HLine(y=3, text='Inflation target')
_vline = imfplotly.VLine(x='2020-06', text='start period', col=1)
_hrect = imfplotly.HRect(y0=2.5, y1=4.5, text='Inflation target range', col=1)
_vrect = imfplotly.VRect(x0='2020-07', x1='2021-01', text='Focus period', col=2)
fig = imfplotly.create_fig_2col(df,
                                linecolslist=linecolslist,
                                figtitle=figtitle,
                                legend_title='Seasonally Adjusted',
                                dict_colors=dict_colors,
                                xhoverformat='%Y %m',
                                xrange=25,
                                yrangelist=[[0,10], None, [2.5, 10], [3, 5]],
                                hlines=[_hline],
                                vlines=[_vline],
                                hrects=[_hrect],
                                vrects=[_vrect])

# Fill between
fig = imfplotly.add_fill(df, df.columns[0], df.columns[1],
                         fig=fig, col=1)

objects.append(fig)

# -----------------------------------------------------
# Create table
table = imfplotly.create_table(df, nperiods=30)
objects.append(table)

# -----------------------------------------------------
# Create output HTML file
outfilename = 'out_Mexico_inflation.html'
title = 'Mexico Inflation'
imfplotly.create_html(outfilename, objects,
                      title=title, datafilename=infilename,
                      links=backlink,
                      show=False)
links[title] = outfilename

#--------------------------------------------------------------------
# Costa Rica Financial
#--------------------------------------------------------------------
objects = []
infilename = 'data/CostaRica_embi.csv'
df = imfplotly.read_csv_data(infilename)
dict_colors = {df.columns[0] : {'color' : 'red'},
               df.columns[1] : {'color' : 'black'}}
dict_markers = {df.columns[0] : {'opacity' : 0}}

# -----------------------------------------------------
# Create 2-col chart
figtitle = 'Costa Rica EMBI (daily)'
linecols = df.columns[0]
fig = imfplotly.create_fig(df, linecols=df.columns[0],
                           barcols=df.columns[1:],
                           figtitle=figtitle,
                           dict_colors=dict_colors,
                           dict_markers=dict_markers,
                           hover_prec=3,
                           xrange='2018-01:')
objects.append(fig)

# -----------------------------------------------------
# Create table
table = imfplotly.create_table(df, nperiods=30)
objects.append(table)

# -----------------------------------------------------
# Create output HTML file
outfilename = 'out_CostaRica.html'
title = 'Costa Rica EMBI'
imfplotly.create_html(outfilename, objects,
                      title=title, datafilename=infilename,
                      links=backlink,
                      show=False)
links[title] = outfilename

#--------------------------------------------------------------------
# 
#--------------------------------------------------------------------
objects = []
infilename = 'data/Nicaragua_remittances.csv'
df = imfplotly.read_csv_data(infilename)
dict_colors={df.columns[0] : {'color' : 'black'}}
# -----------------------------------------------------
# Create lines + bars
figtitle = 'Nicaragua Remittances'
linecols = df.columns[0]
fig = imfplotly.create_fig(df,
                           linecols=linecols,
                           barcols=df.columns[1],
                           figtitle=figtitle,
                           dict_colors=dict_colors,
                           dict_patterns={df.columns[1] : {'shape' : '+', 'size' : 5, 'fgcolor' : 'red', 'fgopacity' : 1}},
                           stack=False,
                           bar_right=True,
                           hover_prec=3,
                           # barwidth=1000*3600*24*10, # 10 days
                           xhoverformat='%Y-%m',
                           xrange=30)
objects.append(fig)

# -----------------------------------------------------
# Create table
table = imfplotly.create_table(df, nperiods=30)
objects.append(table)

# Create bokeh table
table = imfplotly.create_bokeh_table(df)
objects.append(table)

# -----------------------------------------------------
# Create output HTML file
outfilename = 'out_line_bar.html'
title = 'Nicaragua Remittances'
imfplotly.create_html(outfilename, objects,
                      title=title, datafilename=infilename,
                      links=backlink,
                      show=False)
links[title] = outfilename

#--------------------------------------------------------------------
# Create master file
#--------------------------------------------------------------------
imfplotly.create_html(masterfilename,
                      title='Example Report',
                      links=links)
