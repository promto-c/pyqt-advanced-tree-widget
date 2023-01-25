import os, re, sys
from typing import Dict, List

from xml.etree import ElementTree

from PyQt5 import QtGui, QtCore, QtSvg, QtWidgets

TABLER_ICONS_SVG_DIRECTORY = 'tabler-icons\icons'

class TablerQIcon:
    ''' A class that loads icons from the tabler-icons/icons directory and makes them available as attributes.

    Attributes:
        _icon_name_to_path_dict (dict): A dictionary containing the icon name as key and the icon path as value.
        _color (QtGui.QColor): The color of the icon.
        _size (int): The size of the icon.
        _view_box_size (int): The size of the icon's view box.
        _stroke_width (int): The width of the icon's stroke.
        _opacity (float): The opacity of the icon.
    '''
    # Create an instance of QPalette
    _palette = QtGui.QPalette()
    # Get the default color (text color) of the palette and store it in the _default_color attribute
    _default_color = _palette.color(QtGui.QPalette.Text)

    def __init__(self, color: QtGui.QColor=_default_color, size: int=24, view_box_size: int=24, stroke_width: int=2, opacity: float=1.0 ):
        ''' Initialize the widget and load the icons from the tabler-icons/icons directory.
            Args:
                color (QtGui.QColor): color of the icon
                size (int): size of the icon 
                view_box_size (int): size of the view box of the icon
                stroke_width (int): width of the stroke of the icon
                opacity (float): opacity of the icon
        '''
        # Save the properties
        self._color = color
        self._size = size
        self._view_box_size = view_box_size
        self._stroke_width = stroke_width
        self._opacity = opacity

        # Get the icon name to path dictionary  and store it in the _icon_name_to_path_dict attribute
        self._icon_name_to_path_dict = self.get_icon_name_to_path_dict()

    def __getattr__(self, name: str) -> QtGui.QIcon:

        ''' Allows access to the icons as attributes by returning a QIcon object for a given icon name.
            Args:
                name (str): The name of the icon to retrieve.
            Returns:
                QIcon : QIcon object for the given icon name
        '''
        # Get the path of the icon from the dictionary using the name as the key
        svg_icon_path = self._icon_name_to_path_dict.get(name)

        # Return empty qicon if the icon doesn't exist in the dictionary
        if not svg_icon_path:
            return QtGui.QIcon()

        # Load the original SVG file
        with open(svg_icon_path, 'r') as svg_file:
            svg_str = svg_file.read()

        # Parse the SVG file as XML
        svg = ElementTree.fromstring(svg_str)
        # Set the stroke width of the icon
        svg.set('stroke-width', str(self._stroke_width))
        svg_bytes = ElementTree.tostring(svg)

        # Create a renderer object to render the SVG file
        renderer = QtSvg.QSvgRenderer(svg_bytes)
        # Set the view box size
        renderer.setViewBox( QtCore.QRectF(0, 0, self._view_box_size, self._view_box_size) )

        # Create a QPixmap object to hold the rendered image
        pixmap = QtGui.QPixmap(self._size, self._size)
        # Fill the pixmap with transparent color
        pixmap.fill(QtCore.Qt.transparent)
        
        # Create a QPainter object to draw on the QPixmap
        painter = QtGui.QPainter(pixmap)
        # Render the SVG file to the pixmap
        renderer.render(painter)
        
        # Set the opacity of the icon
        painter.setOpacity(self._opacity)
        # Set the composition mode to "SourceIn" to composite the color on the icon
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
        
        # Fill the pixmap with the specified color
        painter.fillRect(pixmap.rect(), self._color )
        
        # End the painter
        painter.end()

        # Create a QIcon object using the rendered image       
        icon = QtGui.QIcon(pixmap)

        # return the icon
        return icon
    
    @classmethod
    def get_icon_name_to_path_dict(cls) -> Dict[str, str]:
        ''' Returns a dictionary containing the icon name as key and the icon path as value.
        
            Returns:
                dict: containing the icon name as key and the icon path as value
        '''
        # Create an empty dictionary to store the icon name and path
        icon_name_to_path_dict = dict()
        # Get a list of all SVG files in the TABLER_ICONS_SVG_DIRECTORY
        svg_file = [ file for file in os.listdir(TABLER_ICONS_SVG_DIRECTORY) if file.endswith('.svg') ]
        
        for file in svg_file:
            # Use regex to replace invalid characters with an underscore
            icon_name = re.sub(r'[^a-zA-Z0-9_]', '_', file.split('.')[0])

            # Prepend an underscore to the icon name if it starts with a number
            if icon_name[0].isdigit():
                icon_name = "_" + icon_name
                
            # Join the directory path and the file name to get the full path of the icon file
            icon_path = os.path.join(TABLER_ICONS_SVG_DIRECTORY, file)
            # Add the icon name and path to the icon_name_to_path_dict
            icon_name_to_path_dict[icon_name] = icon_path

        # return the dictionary containing the icon name and path
        return icon_name_to_path_dict
    
    @classmethod
    def get_icon_name_list(cls) -> List[str]:
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

    # Create instance
    tabler_qicon = TablerQIcon()
    
    # Check attribute
    icon_users = tabler_qicon.users # output <PyQt5.QtGui.QIcon object at 0x...>
