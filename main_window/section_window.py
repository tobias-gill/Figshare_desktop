"""

"""


from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QMdiSubWindow)
from PyQt5.QtCore import (Qt)

from Figshare_desktop.formatting.formatting import scaling_ratio
from Figshare_desktop.formatting.formatting import checkable_button

from Figshare_desktop.projects_windows.projects_window import ProjectsWindow
from Figshare_desktop.data_window.data_window import DataWindow
from Figshare_desktop.selection_window.selection_window import SelectionWindow

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class sectionWindow(QMdiSubWindow):
    """
    Creates the beginning window from which the different Figshare structures can be navigated to
    """

    def __init__(self, app, OAuth_token, parent):
        """

        :param app: QApplication object
        :param OAuth_token: Figshare OAuth token
        :param parent: QMDI object that is the overall parent of the application
        """
        super().__init__()

        self.app = app
        self.token = OAuth_token
        self.parent = parent

        self.open_windows = self.parent.open_windows

        self.initUI()

    def initUI(self):
        """
        User Interface initialization
        :return:
        """
        self.format_window()
        self.w = QWidget()
        self.w.setLayout(self.button_layout())
        self.setWidget(self.w)

    def format_window(self):
        """
        Formats the sections window
        """
        self.setWindowFlags(Qt.FramelessWindowHint)
        w_scale, f_scale = scaling_ratio(self.app)

        # Gets the QRect of the main window
        geom = self.parent.geometry()

        # Define geometries for the section window
        x0 = geom.x()
        y0 = geom.y()
        w = ((geom.width() / 8) - x0)
        h = (geom.height() - y0)
        self.setGeometry(x0, y0, w, h)

        # Store the section window geometry in the main window
        self.parent.section_geom = self.geometry()


    def button_layout(self):
        """
        Creates a QLayout object holding the section buttons
        :return: QLayout Object containing toggle buttons for different sections
        """
        # QLayout to hold buttons
        button_box = QVBoxLayout()

        # Projects
        projects_btn = QPushButton('Projects', self)
        checkable_button(self.app, projects_btn)
        projects_btn.clicked[bool].connect(self.on_projects_btn_pressed)

        # Collections
        collections_btn = QPushButton('Collections', self)
        checkable_button(self.app, collections_btn)

        # Local Data
        localdata_btn = QPushButton('Local Data', self)
        checkable_button(self.app, localdata_btn)

        # Selection
        selection_btn = QPushButton('Selection', self)
        checkable_button(self.app, selection_btn)

        # Add Buttons to Layout
        button_box.addWidget(projects_btn)
        button_box.addWidget(collections_btn)
        button_box.addWidget(localdata_btn)
        button_box.addWidget(selection_btn)

        return button_box

    def on_projects_btn_pressed(self):
        """
        Called when the projects button is pressed. Is also called after some project information edits.
        """
        # Check to see if the projects window is already open
        if 'projects_window' in self.open_windows:
            self.open_windows.remove('projects_window')
            self.parent.projects_window.close()

            # Check to see if a project information window is open
            if 'project_info_window' in self.open_windows:
                self.open_windows.remove('project_info_window')
                self.parent.project_info_window.close()

            # Check to see if a project articles window is open
            if 'project_articles_window' in self.open_windows:
                self.open_windows.remove('project_articles_window')
                self.parent.project_articles_window.close()

        # Check to see if the create new project window is open
        elif 'new_project_window' in self.open_windows:
            self.open_windows.remove('new_project_window')
            self.parent.new_project_window.close()

        # If no projects windows are open then create a projects window and show
        elif 'projects_window' not in self.open_windows and 'new_project_window' not in self.open_windows:
            self.open_windows.add('projects_window')
            self.parent.projects_window = ProjectsWindow(self.app, self.token, self.parent)
            self.parent.mdi.addSubWindow(self.parent.projects_window)
            self.parent.projects_window.show()
