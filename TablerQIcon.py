import os, re, sys
from xml.etree import ElementTree

from PyQt5 import QtGui, QtCore, QtSvg, QtWidgets

TABLER_ICONS_SVG_DIRECTORY = 'tabler-icons\icons'

class TablerQIcon:
    ''' A class that loads icons from the tabler-icons/icons directory and makes them available as attributes.

    Attributes:
        _icon_name_to_path_dict (dict): A dictionary containing the icon name as key and the icon path as value.
    '''
    palette = QtGui.QPalette()
    
    color = palette.color(QtGui.QPalette.Text)

    def __init__(self, color: QtGui.QColor=color, size=24, view_box_size=24, stroke_width=2, opacity=1.0 ):
        ''' Initialize the widget and load the icons from the tabler-icons/icons directory.
        '''

        self._color = color
        self._size = size
        self._view_box_size = view_box_size
        self._stroke_width = stroke_width
        self._opacity = opacity

        self._icon_name_to_path_dict = self.get_icon_name_to_path_dict()

    def __getattr__(self, name: str) -> QtGui.QIcon:

        ''' Allows access to the icons as attributes by returning a QIcon object for a given icon name.
            Args:
                name (str): The name of the icon to retrieve.
            Returns:
                QIcon : QIcon object for the given icon name
        '''

        svg_icon_path = self._icon_name_to_path_dict.get(name)

        if not svg_icon_path:
            return

        # Load the original SVG file
        with open(svg_icon_path, 'r') as svg_file:
            svg_str = svg_file.read()

        # parse the SVG file as XML
        svg = ElementTree.fromstring(svg_str)
        svg.set('stroke-width', str(self._stroke_width))
        svg_bytes = ElementTree.tostring(svg)

        renderer = QtSvg.QSvgRenderer(svg_bytes)
        renderer.setViewBox( QtCore.QRectF(0, 0, self._view_box_size, self._view_box_size) )

        pixmap = QtGui.QPixmap(self._size, self._size)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        renderer.render(painter)
        
        painter.setOpacity(self._opacity)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
        
        painter.fillRect(pixmap.rect(), self._color )
        
        painter.end()

        icon = QtGui.QIcon(pixmap)
        return(icon)
    
    @classmethod
    def get_icon_name_to_path_dict(cls):
        icon_name_to_path_dict = dict()
        svg_file = [ file for file in os.listdir(TABLER_ICONS_SVG_DIRECTORY) if file.endswith('.svg') ]
        
        for file in svg_file:
            # Use regex to replace invalid characters with an underscore
            icon_name = re.sub(r'[^a-zA-Z0-9_]', '_', file.split('.')[0])

            # prepend an underscore to the icon name if it starts with a number
            if icon_name[0].isdigit():
                icon_name = "_" + icon_name
                
            # join the directory path and the file name to get the full path of the icon file
            icon_path = os.path.join(TABLER_ICONS_SVG_DIRECTORY, file)
            # add the icon name and path to the icon_name_to_path_dict
            icon_name_to_path_dict[icon_name] = icon_path
        return icon_name_to_path_dict
    
    @classmethod
    def get_icon_name_list(cls) -> list:
        ''' Returns a list of all the available icon names.
        '''
        icon_name_to_path_dict = cls.get_icon_name_to_path_dict()
        return list(icon_name_to_path_dict.keys())
    
    @classmethod
    def get_icon_path(cls, name: str) -> str:
        ''' Returns a icon path from input name.
        '''
        icon_name_to_path_dict = cls.get_icon_name_to_path_dict()
        return icon_name_to_path_dict.get(name)

if __name__ == '__main__':
    # Create the application
    app = QtWidgets.QApplication(sys.argv)

    # create instance
    tabler_qicon = TablerQIcon()
    
    # check attribute
    icon_users = tabler_qicon.users # output <PyQt5.QtGui.QIcon object at 0x...>
