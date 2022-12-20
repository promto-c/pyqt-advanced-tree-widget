
import os

THEME_PATH = os.path.dirname( os.path.abspath(__file__) )

STYLE_SHEET_PATH_DICT = {
    'dark': os.path.join( THEME_PATH, 'dark_theme.css' )
}

def setTheme( app, theme='default' ):
    ''' This function use to set theme for "QApplication", support for "PySide2" and "PyQt5"
    '''

    lib_name =app.__module__.split('.')[0]

    QtGui = __import__(lib_name).QtGui

    if theme == 'dark':
        app.setStyle('Fusion')

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

        app.setPalette(palette)

        # set dark theme style sheet
        with open( STYLE_SHEET_PATH_DICT[theme], 'r' ) as style_sheet:
            app.setStyleSheet( style_sheet.read() )
    
    elif theme == 'default':
        app.setStyle(str)
        app.setPalette( QtGui.QPalette() )

def setMatplotlibDarkTheme():

    import matplotlib
    import matplotlib.pyplot as plt

    plt.style.use('dark_background')

    matplotlib.rcParams['axes.edgecolor'] = (0.4, 0.4, 0.4)
    matplotlib.rcParams['xtick.color'] = (0.56, 0.56, 0.56)
    matplotlib.rcParams['ytick.color'] = (0.56, 0.56, 0.56)
