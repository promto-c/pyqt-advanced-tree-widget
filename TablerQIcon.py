import os
import re
from PyQt5 import QtGui

TABLER_ICONS_SVG_DIRECTORY = 'tabler-icons\icons'

class TablerQIcon:
    ''' A class that loads icons from the tabler-icons/icons directory and makes them available as attributes.

    Attributes:
        icon_dict (dict): A dictionary containing the icon name as key and the icon path as value.
    '''
    icon_dict: dict = dict()

    def __init__(self):
        ''' Initialize the widget and load the icons from the tabler-icons/icons directory.
        '''
        svg_file = [ file for file in os.listdir(TABLER_ICONS_SVG_DIRECTORY) if file.endswith('.svg') ]
        
        for file in svg_file:
            # Use regex to replace invalid characters with an underscore
            icon_name = re.sub(r'[^a-zA-Z0-9_]', '_', file.split('.')[0])

            # prepend an underscore to the icon name if it starts with a number
            if icon_name[0].isdigit():
                icon_name = "_" + icon_name
                
            # join the directory path and the file name to get the full path of the icon file
            icon_path = os.path.join(TABLER_ICONS_SVG_DIRECTORY, file)
            # add the icon name and path to the icon_dict
            self.icon_dict[icon_name] = icon_path
 
    def __getattr__(self, name: str) -> QtGui.QIcon:
        ''' Allows access to the icons as attributes by returning a QIcon object for a given icon name.
            Args:
                name (str): The name of the icon to retrieve.
            Returns:
                QIcon : QIcon object for the given icon name
        '''
        return QtGui.QIcon(self.icon_dict.get(name))

if __name__ == '__main__':
    # create instance
    tabler_qicon = TablerQIcon()
    # check attribute
    icon_users = tabler_qicon.users # output <PyQt5.QtGui.QIcon object at 0x...>
