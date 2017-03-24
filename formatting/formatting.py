"""

"""

import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QToolTip, QMessageBox, QMainWindow,
                             QAction, qApp, QHBoxLayout, QVBoxLayout, QSizePolicy, QShortcut)
from PyQt5.QtGui import (QIcon, QFont, QKeySequence)
from PyQt5.QtCore import (Qt)

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"

def scaling_ratio(app):
    """
    Determines a scaling ratio for window and font sizes
    :param app: QApplication object
    :return: nothing
    """

    # Reference Sizes
    ref_dpi = 144.
    ref_height = 1020
    ref_width = 1920

    # Current Device Sizes
    dpi = app.primaryScreen().logicalDotsPerInch()
    geom = app.primaryScreen().availableGeometry()
    height = geom.height()
    width = geom.width()

    # Size Ratios
    m_ratio = min(height/ref_height, width/ref_width)
    m_ratiofont = min(height*ref_dpi/(dpi*ref_height),
                      width*ref_dpi/(dpi*ref_width))

    # Check to see if the ratio is too small
    if m_ratio < 1:
        m_ratio = 1
    if m_ratiofont < 1:
        m_ratiofont = 1

    return m_ratio, m_ratiofont


def button_font(app):
    """
    Returns a QFont object for buttons
    :param app: QApplication object
    :return: QFont object
    """

    # Gets window and font ratios
    screen_ratio, font_ratio = scaling_ratio(app)

    # Reference font size
    ref_fontsize = 17

    # Scale font size
    fontsize = font_ratio * ref_fontsize

    # Create and modify QFont object
    font = QFont('SansSerif')
    font.setBold(True)
    font.setPointSize(fontsize)

    return font

def search_font(app):
    """
    Returns a QFont object for search bars
    :param app: QApplication object
    :return: QFont object
    """

    # Gets window and font ratios
    screen_ratio, font_ratio = scaling_ratio(app)

    # Reference font size
    ref_fontsize = 11

    # Scale font size
    fontsize = font_ratio * ref_fontsize

    # Create and modify QFont object
    font = QFont('SansSerif')
    font.setBold(False)
    font.setPointSize(fontsize)

    return font


def checkable_button(app, button):
    """
    Formats a QPushButton to be checkable
    :param app: QApplication object
    :param button: QPushButton
    :return:
    """
    button.setCheckable(True)
    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    button.setFont(button_font(app))


def press_button(app, button):
    """
    Formats a QPushButton
    :param app: QApplication object
    :param button: QPushButton
    :return:
    """
    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    button.setFont(button_font(app))


def search_bar(app, lineedit):
    """
    Formats a QLineEdit object for with a search bar style
    :param app: QApplication object
    :param lineedit: QLineEdit object to be styled
    :return:
    """
    lineedit.sizeHint()
    lineedit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
    lineedit.setFont(search_font(app))