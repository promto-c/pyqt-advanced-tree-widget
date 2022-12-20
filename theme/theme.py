
import os

THEME_PATH = os.path.dirname(os.path.abspath(__file__))

STYLE_SHEET_PATH_DICT = {
    'dark': os.path.join(THEME_PATH, 'dark_theme.css')
}

def setTheme(app, theme: str='default') -> None:
    ''' This function use to set theme for "QApplication", support for "PySide2" and "PyQt5"
    '''

    # Get the name of the library that the app object belongs to
    lib_name = app.__module__.split('.')[0]

    # Import the QtGui module from the library with the name stored in lib_name
    QtGui = __import__(lib_name).QtGui

    # Check if the theme is set to 'dark'
    if theme == 'dark':
        # Set the application style to 'Fusion'
        app.setStyle('Fusion')

        # Create a palette with dark colors
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(44, 44, 44))
        palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(246, 246, 246))
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(29, 29, 29))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(0, 0, 0))
        palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(210, 210, 210))
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(210, 218, 218))
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(44, 44, 44))
        palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(210, 210, 210))
        palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(246, 0, 0))
        palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(110, 120, 125))
        # Apply the dark palette to the application
        app.setPalette(palette)

        # set dark theme style sheet
        with open(STYLE_SHEET_PATH_DICT[theme], 'r') as style_sheet:
            app.setStyleSheet(style_sheet.read())
    
    # Check if the theme is set to 'default'
    elif theme == 'default':
        # Set the application style to an empty string, which resets it to the default style
        app.setStyle(str())

        # Reset the application palette to the default palette
        app.setPalette(QtGui.QPalette())

def setMatplotlibDarkTheme() -> None:
    ''' This function sets the theme of Matplotlib plots to a dark theme.
    '''
    # Import the Matplotlib library and the Pyplot submodule
    import matplotlib
    import matplotlib.pyplot as plt

    # Set the Matplotlib style to the 'dark_background' style
    plt.style.use('dark_background')

    # Set the color of the axes edges to a dark gray color
    matplotlib.rcParams['axes.edgecolor'] = (0.4, 0.4, 0.4)

    # Set the color of the x-axis tick labels to a light gray color
    matplotlib.rcParams['xtick.color'] = (0.56, 0.56, 0.56)

    # Set the color of the y-axis tick labels to a light gray color
    matplotlib.rcParams['ytick.color'] = (0.56, 0.56, 0.56)
