import os
import re
from PyQt5 import QtGui

TABLER_ICONS_SVG_DIRECTORY = 'tabler-icons\icons'

class TablerQIcon:

    icon_dict: dict = dict()

    def __init__(self):

        for file in os.listdir(TABLER_ICONS_SVG_DIRECTORY):
            
            if file.endswith('.svg'):

                icon_name = file.split('.')[0]
                # Use regex to replace invalid characters with an underscore
                icon_name = re.sub(r'[^a-zA-Z0-9_]', '_', icon_name)
                icon_path = os.path.join(TABLER_ICONS_SVG_DIRECTORY, file)

                self.icon_dict[icon_name] = icon_path
 
    def __getattr__(self, name):

        if name in self.icon_dict.keys():
            icon_path = self.icon_dict[name]
            return QtGui.QIcon(icon_path)

if __name__ == '__main__':

    # create instance
    tabler_qicon = TablerQIcon()

    # check attribute
    icon_users = tabler_qicon.users # output <PyQt5.QtGui.QIcon object at 0x...>
