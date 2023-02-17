'''
Collection of class objects to be used to generate plotly output.
'''

import os
import sys
import shutil
import markdown

class HLine:
    '''
    Class HLine for horizontal lines.
    '''

    def __init__(self,**kwargs):
        self.name = 'HLINE'
        # Initialize all internal params and update with kwards
        self.y = 0
        self.line_width = 3
        self.line_color = 'red'
        self.line_dash = 'dash'
        self.opacity = 0.6
        self.text = ''
        self.position = 'top left'
        self.font_size = 18
        self.font_color = 'red'
        self.font_opacity = 0.8
        self.font_family = 'Open Sans'
        self.row = 'all'
        self.col = 'all'
        self.secondary_y = False
        
        if 'y' in kwargs:
            self.y = kwargs['y']
        if 'line_width' in kwargs:
            self.line_width = kwargs['line_width']
        if 'line_color' in kwargs:
            self.line_color = kwargs['line_color']
        if 'line_dash' in kwargs:
            self.line_dash = kwargs['line_dash']
        if 'opacity' in kwargs:
            self.opacity = kwargs['opacity']
        if 'text' in kwargs:
            self.text = kwargs['text']
        if 'position' in kwargs:
            self.position = kwargs['position']
        if 'font_size' in kwargs:
            self.font_size = kwargs['font_size']
        if 'font_color' in kwargs:
            self.font_color = kwargs['font_color']
        if 'font_opacity' in kwargs:
            self.font_opacity = kwargs['font_opacity']
        if 'font_family' in kwargs:
            self.font_family = kwargs['font_family']
        if 'row' in kwargs:
            self.row = kwargs['row']
        if 'col' in kwargs:
            self.col = kwargs['col']
        if 'secondary_y' in kwargs:
            self.secondary_y = kwargs['secondary_y']
            
    def __str__(self):
        printstrs = 'HLine(y=' + str(self.y) + ', line_width=' + str(self.line_width) + ',\n'
        printstrs += 'line_dash=' + str(self.line_dash) + ',\n'
        printstrs += 'line_color=' + str(self.line_color) + ', opacity=' + str(self.opacity) + ',\n'
        printstrs += 'text=' + str(self.text) + ', position="' + str(self.position) + '",\n'
        printstrs += 'font_size=' + str(self.font_size) + ', font_color=' + str(self.font_color) + ',\n'
        printstrs += 'font_opacity=' + str(self.font_opacity) + ', font_family=' + str(self.font_family) + ',\n'
        printstrs += 'row=' + str(self.row) + ', col=' + str(self.col) + ', secondary_y=' + str(self.secondary_y) + ')'
        return printstrs
    
class VLine:
    '''
    Class VLine for vertical lines.
    '''

    def __init__(self,**kwargs):
        self.name = 'VLINE'
        # Initialize all internal params and update with kwards
        self.x = 0
        self.line_width = 3
        self.line_dash = 'dash'
        self.line_color = 'red'
        self.opacity = 0.6
        self.text = ''
        self.position = 'top left'
        self.font_size = 18
        self.font_color = 'red'
        self.font_opacity = 0.8
        self.font_family = 'Open Sans'
        self.row = 'all'
        self.col = 'all'
        self.secondary_y = False
        
        if 'x' in kwargs:
            self.x = kwargs['x']
        if 'line_width' in kwargs:
            self.line_width = kwargs['line_width']
        if 'line_dash' in kwargs:
            self.line_dash = kwargs['line_dash']
        if 'line_color' in kwargs:
            self.line_color = kwargs['line_color']
        if 'opacity' in kwargs:
            self.opacity = kwargs['opacity']
        if 'text' in kwargs:
            self.text = kwargs['text']
        if 'position' in kwargs:
            self.position = kwargs['position']
        if 'font_size' in kwargs:
            self.font_size = kwargs['font_size']
        if 'font_color' in kwargs:
            self.font_color = kwargs['font_color']
        if 'font_opacity' in kwargs:
            self.font_opacity = kwargs['font_opacity']
        if 'font_family' in kwargs:
            self.font_family = kwargs['font_family']
        if 'row' in kwargs:
            self.row = kwargs['row']
        if 'col' in kwargs:
            self.col = kwargs['col']
        if 'secondary_y' in kwargs:
            self.secondary_y = kwargs['secondary_y']
            
    def __str__(self):
        printstrs = 'VLine(x=' + str(self.x) + ', line_width=' + str(self.line_width) + ',\n'
        printstrs += 'line_dash=' + str(self.line_dash) + ',\n'
        printstrs += 'line_color=' + str(self.line_color) + ', opacity=' + str(self.opacity) + ',\n'
        printstrs += 'text=' + str(self.text) + ', position="' + str(self.position) + '",\n'
        printstrs += 'font_size=' + str(self.font_size) + ', font_color=' + str(self.font_color) + ',\n'
        printstrs += 'font_opacity=' + str(self.font_opacity) + ', font_family=' + str(self.font_family) + ',\n'
        printstrs += 'row=' + str(self.row) + ', col=' + str(self.col) + ', secondary_y=' + str(self.secondary_y) + ')'
        return printstrs

class HRect:
    '''
    Class HRect for horizontal rectangles.
    '''

    def __init__(self,**kwargs):
        self.name = 'HRECT'
        # Initialize all internal params and update with kwards
        self.y0 = 0
        self.y1 = 1
        self.line_width = 0
        self.line_dash = 'dash'
        self.line_color = 'orange'
        self.fill_color = 'orange'
        self.opacity = 0.6
        self.text = ''
        self.position = 'top left'
        self.font_size = 18
        self.font_color = 'red'
        self.font_opacity = 0.8
        self.font_family = 'Open Sans'
        self.row = 'all'
        self.col = 'all'
        self.secondary_y = False
        
        if 'y0' in kwargs:
            self.y0 = kwargs['y0']
        if 'y1' in kwargs:
            self.y1 = kwargs['y1']
        if 'line_width' in kwargs:
            self.line_width = kwargs['line_width']
        if 'line_dash' in kwargs:
            self.line_dash = kwargs['line_dash']
        if 'line_color' in kwargs:
            self.line_color = kwargs['line_color']
        if 'fill_color' in kwargs:
            self.fill_color = kwargs['fill_color']
        if 'opacity' in kwargs:
            self.opacity = kwargs['opacity']
        if 'text' in kwargs:
            self.text = kwargs['text']
        if 'position' in kwargs:
            self.position = kwargs['position']
        if 'font_size' in kwargs:
            self.font_size = kwargs['font_size']
        if 'font_color' in kwargs:
            self.font_color = kwargs['font_color']
        if 'font_opacity' in kwargs:
            self.font_opacity = kwargs['font_opacity']
        if 'font_family' in kwargs:
            self.font_family = kwargs['font_family']
        if 'row' in kwargs:
            self.row = kwargs['row']
        if 'col' in kwargs:
            self.col = kwargs['col']
        if 'secondary_y' in kwargs:
            self.secondary_y = kwargs['secondary_y']
            
    def __str__(self):
        printstrs = 'HRect(y0=' + str(self.y0) + ', y1=' + str(self.y1) + ', line_width=' + str(self.line_width) + ',\n'
        printstrs += 'line_dash=' + str(self.line_dash) + 'line_color=' + str(self.line_color) + ',\n'
        printstrs += 'fill_color=' + str(self.fill_color) + ', opacity=' + str(self.opacity) + ',\n'
        printstrs += 'text=' + str(self.text) + ', position="' + str(self.position) + '",\n'
        printstrs += 'font_size=' + str(self.font_size) + ', font_color=' + str(self.font_color) + ',\n'
        printstrs += 'font_opacity=' + str(self.font_opacity) + ', font_family=' + str(self.font_family) + ',\n'
        printstrs += 'row=' + str(self.row) + ', col=' + str(self.col) + ', secondary_y=' + str(self.secondary_y) + ')'
        return printstrs

class VRect:
    '''
    Class VRect for vertical rectangles.
    '''

    def __init__(self,**kwargs):
        self.name = 'VRECT'
        # Initialize all internal params and update with kwards
        self.x0 = 0
        self.x1 = 1
        self.line_width = 0
        self.line_dash = 'dash'
        self.line_color = 'orange'
        self.fill_color = 'orange'
        self.opacity = 0.6
        self.text = ''
        self.position = 'top left'
        self.font_size = 18
        self.font_color = 'red'
        self.font_opacity = 0.8
        self.font_family = 'Open Sans'
        self.row = 'all'
        self.col = 'all'
        self.secondary_y = False
        
        if 'x0' in kwargs:
            self.x0 = kwargs['x0']
        if 'x1' in kwargs:
            self.x1 = kwargs['x1']
        if 'line_width' in kwargs:
            self.line_width = kwargs['line_width']
        if 'line_dash' in kwargs:
            self.line_dash = kwargs['line_dash']
        if 'line_color' in kwargs:
            self.line_color = kwargs['line_color']
        if 'fill_color' in kwargs:
            self.fill_color = kwargs['fill_color']
        if 'opacity' in kwargs:
            self.opacity = kwargs['opacity']
        if 'text' in kwargs:
            self.text = kwargs['text']
        if 'position' in kwargs:
            self.position = kwargs['position']
        if 'font_size' in kwargs:
            self.font_size = kwargs['font_size']
        if 'font_color' in kwargs:
            self.font_color = kwargs['font_color']
        if 'font_opacity' in kwargs:
            self.font_opacity = kwargs['font_opacity']
        if 'font_family' in kwargs:
            self.font_family = kwargs['font_family']
        if 'row' in kwargs:
            self.row = kwargs['row']
        if 'col' in kwargs:
            self.col = kwargs['col']
        if 'secondary_y' in kwargs:
            self.secondary_y = kwargs['secondary_y']
            
    def __str__(self):
        printstrs = 'VRect(x0=' + str(self.x0) + ', x1=' + str(self.x1) + ', line_width=' + str(self.line_width) + ',\n'
        printstrs += 'line_dash=' + str(self.line_dash) + 'line_color=' + str(self.line_color) + ',\n'
        printstrs += 'fill_color=' + str(self.fill_color) + ', opacity=' + str(self.opacity) + ',\n'
        printstrs += 'text=' + str(self.text) + ', position="' + str(self.position) + '",\n'
        printstrs += 'font_size=' + str(self.font_size) + ', font_color=' + str(self.font_color) + ',\n'
        printstrs += 'font_opacity=' + str(self.font_opacity) + ', font_family=' + str(self.font_family) + ',\n'
        printstrs += 'row=' + str(self.row) + ', col=' + str(self.col) + ', secondary_y=' + str(self.secondary_y) + ')'
        return printstrs

class Space:
    '''
    Class Space for vertical spaces in HTML.
    '''

    def __init__(self, vspace=0):
        self.name = 'SPACE'
        # Initialize
        self.vspace = vspace
        
    def __str__(self):
        printstrs = 'Space(vspace=' + str(self.vspace) + ')'
        return printstrs

    def to_html(self):
        '''
        Generate HTML str that can be inserted.
        '''

        # Just create a <p> with margin-bottom set to vspace
        html_str = '''\n\n<p style="margin-bottom:''' + str(self.vspace) + '''in;"></p>\n\n'''

        return html_str
    
class Heading:
    '''
    Class Heading1 for heading text in HTML.
    '''

    def __init__(self, text='', fontsize=14, fontcolor='black', bold=False, italic=False):
        self.name = 'HEADING'
        # Initialize
        self.text = text
        self.fontsize = fontsize
        self.fontcolor = fontcolor
        self.bold = bold
        self.italic = italic
        
    def __str__(self):
        printstrs = 'Heading(text=' + str(self.text) + ', fontsize=' + str(self.fontsize) + ',' \
            + 'bold=' +str(self.bold) + ', italic=' + str(self.italic) + ', fontcolor=' + str(self.fontcolor) + ')'
        return printstrs

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, _text):
        self._text = _text

    @property
    def fontsize(self):
        return self._fontsize

    @fontsize.setter
    def fontsize(self, _fontsize):
        self._fontsize = _fontsize

    @property
    def fontcolor(self):
        return self._fontcolor

    @fontcolor.setter
    def fontcolor(self, _fontcolor):
        self._fontcolor = _fontcolor
        
    @property
    def bold(self):
        return self._bold

    @bold.setter
    def bold(self, _bold):
        self._bold = _bold

    @property
    def italic(self):
        return self._italic

    @italic.setter
    def italic(self, _italic):
        self._italic = _italic
        
    def to_html(self):
        '''
        Generate HTML str that can be inserted.
        '''

        # Just create a <p> with formatting
        html_str = '''\n\n<p style="color:''' + self.fontcolor + ''';font-size:''' + str(self.fontsize) + '''pt;">'''
        if self.bold:
            html_str += '<b>'
        if self.italic:
            html_str += '<i>'

        # Add text
        html_str += self.text
        
        if self.bold:
            html_str += '</b>'
        if self.italic:
            html_str += '</i>'
        html_str += '''</p>\n\n'''

        return html_str

class Heading1(Heading):
    '''
    Class Heading1 for heading text in HTML.
    '''

    def __init__(self, text='', fontsize=25, fontcolor='black', bold=False, italic=False):
        Heading.__init__(self, text=text, fontsize=fontsize, fontcolor=fontcolor, bold=bold, italic=italic)
        self.name = 'HEADING1'
        
    def __str__(self):
        printstrs = 'Heading1(text=' + str(self.text) + ', fontsize=' + str(self.fontsize) + ',' \
            + 'bold=' +str(self.bold) + ', italic=' + str(self.italic) + ', fontcolor=' + str(self.fontcolor) + ')'
        return printstrs
    
class Heading2(Heading):
    '''
    Class Heading2 for heading text in HTML.
    '''

    def __init__(self, text='', fontsize=18, fontcolor='black', bold=False, italic=False):
        Heading.__init__(self, text=text, fontsize=fontsize, fontcolor=fontcolor, bold=bold, italic=italic)
        self.name = 'HEADING2'
        
    def __str__(self):
        printstrs = 'Heading2(text=' + str(self.text) + ', fontsize=' + str(self.fontsize) + ',' \
            + 'bold=' +str(self.bold) + ', italic=' + str(self.italic) + ', fontcolor=' + str(self.fontcolor) + ')'
        return printstrs
    
class Heading3(Heading):
    '''
    Class Heading3 for heading text in HTML.
    '''

    def __init__(self, text='', fontsize=12, fontcolor='black', bold=False, italic=False):
        Heading.__init__(self, text=text, fontsize=fontsize, fontcolor=fontcolor, bold=bold, italic=italic)
        self.name = 'HEADING3'
        
    def __str__(self):
        printstrs = 'Heading3(text=' + str(self.text) + ', fontsize=' + str(self.fontsize) + ',' \
            + 'bold=' +str(self.bold) + ', italic=' + str(self.italic) + ', fontcolor=' + str(self.fontcolor) + ')'
        return printstrs

class Markdown:
    '''
    Class Markdown for adding text via markdown.
    '''

    def __init__(self, text=''):
        self.name = 'TEXT'
        # Initialize
        self.text = text
        
    def __str__(self):
        printstrs = 'Markdown(text=' + str(self.text) + ')'
        return printstrs

    def to_html(self):
        '''
        Generate HTML str that can be inserted.
        '''

        # Just create a <p> with markdown output.
        # TODO: Add css flags so text can be formatted.
        markdown_text = markdown.markdown(self.text)
        html_str = '''\n\n<p>''' + markdown_text + '''</p>\n\n'''

        return html_str
    
class NewPage:
    '''
    Class for NewPage object
    '''

    def __init__(self, filename=None, title=''):
        self.objname = 'NEWPAGE'
        self.filename = filename
        self.title = title

    def __str__(self):
        printstrs = 'NewPage(filename="' + str(self.filename) + '",title="' + str(self.title) + '")'
        return printstrs
    
    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, fname):
        self._filename = fname

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, _title):
        self._title = _title
    

class Image:
    '''
    Class Image for png/jpg/svg files in HTML.
    Works with png, jpg, svg files but *not* with PDF files.
    '''

    def __init__(self, srcfile, text='',
                 fontsize=15, fontcolor='black',
                 # quick way to set bold/italic for all text,
                 # can also have <b>, <i> tags within text.
                 bold=False, italic=False,
                 center=False,
                 width=None, height=None,
                 debug=False):
        self.name = 'IMAGE'
        self.debug = debug
        
        # Initialize
        self.srcfile = os.path.abspath(srcfile)
        if not os.path.isfile(srcfile):
            print('File ' + srcfile + ' does not exist')
            sys.exit(-1)
        if self.debug:
            print('srcfile = ' + self.srcfile)
            
        self.text = str(text)
        self.fontsize = fontsize
        self.fontcolor = fontcolor
        self.bold = bold
        self.italic = italic
        self.center = center
        self.width = width
        self.height = height

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, _text):
        self._text = _text

    @property
    def fontsize(self):
        return self._fontsize

    @fontsize.setter
    def fontsize(self, _fontsize):
        self._fontsize = _fontsize

    @property
    def fontcolor(self):
        return self._fontcolor

    @fontcolor.setter
    def fontcolor(self, _fontcolor):
        self._fontcolor = _fontcolor

    @property
    def bold(self):
        return self._bold

    @bold.setter
    def bold(self, _bold):
        self._bold = _bold

    @property
    def italic(self):
        return self._italic

    @italic.setter
    def italic(self, _italic):
        self._italic = _italic
        
    def __str__(self):
        printstrs = 'Image(text=' + self.text + ', width=' + str(self.width) + ', height=' + str(self.height) + ')'
        return printstrs

    def to_html(self, outdir=None):
        '''
        Generate HTML str that can be inserted.

        For the src of <img>, we need to make sure the file exists in the output dir.
        The option outdir can be passed in so that the correct output can be specified.
        In this case the file is copied to the outdir and HTML is generated based on this location.
        '''

        # Just <p> and within add <img> and <p>
        html_str = '''\n\n<p'''
        # If center, add to the outside <p>
        if self.center:
            html_str += ''' style="text-align:center"'''
        html_str += '>'

        # 
        html_str += '''<img src="'''
        if outdir:
            # Create output dir
            if not os.path.isdir(outdir):
                os.makedirs(outdir)
            # Copy the src file
            # The srcfile attribute should be an absolute path
            newfilename = outdir + '/' + os.path.basename(self.srcfile)
            shutil.copy(self.srcfile, newfilename)
            if self.debug:
                print('Copied ' + self.srcfile + ' to ' + newfilename)
            # For the actual link use a relative path to the outdir.
            # This way if the output HTML file and images dir are bundled together
            # they will work together.
            filename = os.path.basename(outdir) + '/' + os.path.basename(self.srcfile)
            html_str +=  filename
        else:
            html_str +=  self.srcfile
        html_str += '''" alt="''' + self.text + '''" style="'''
        if self.width:
            html_str += '''width:''' + str(self.width) + '''px;'''
        if self.height:
            html_str += '''height:''' + str(self.height) + '''px;'''
        html_str += '''">\n'''

        # Add text
        html_str += '''  <p '''
        html_str += '''style="color:''' + self.fontcolor + ''';font-size:''' + str(self.fontsize) + '''pt;'''
        if self.center:
            html_str += ''' text-align:center'''
        html_str += '''">'''            
        
        if self.bold:
            html_str += '<b>'
        if self.italic:
            html_str += '<i>'
        # text
        html_str += self.text
        
        if self.bold:
            html_str += '</b>'
        if self.italic:
            html_str += '</i>'
        html_str += '''</p>\n'''

        # end enclosing <p>
        html_str += '''</p>\n\n'''

        return html_str
