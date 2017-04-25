"""

"""


from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QMdiSubWindow)
from PyQt5.QtCore import (Qt)

from Figshare_desktop.formatting.formatting import scaling_ratio
from Figshare_desktop.formatting.formatting import checkable_button

from Figshare_desktop.projects_windows.projects_window import ProjectsWindow
from Figshare_desktop.collections_windows.collections_window import CollectionsWindow
from Figshare_desktop.data_window.data_window import DataWindow
from Figshare_desktop.data_window.data_articles_window import DataArticlesWindow
from Figshare_desktop.data_window.figshare_add_window import FigshareAddWindow
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

    #####
    # Window Widgets
    #####

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
        self.projects_btn = projects_btn

        # Collections
        collections_btn = QPushButton('Collections', self)
        checkable_button(self.app, collections_btn)
        collections_btn.clicked[bool].connect(self.on_collections_btn_pressed)

        self.collections_btn = collections_btn

        # Local Data
        localdata_btn = QPushButton('Local Data', self)
        checkable_button(self.app, localdata_btn)
        localdata_btn.clicked[bool].connect(self.on_local_data_btn_pressed)
        self.localdata_btn = localdata_btn

        # Selection
        selection_btn = QPushButton('Selection', self)
        checkable_button(self.app, selection_btn)

        self.selection_btn = selection_btn

        # Add Buttons to Layout
        button_box.addWidget(projects_btn)
        button_box.addWidget(collections_btn)
        button_box.addWidget(localdata_btn)
        button_box.addWidget(selection_btn)

        return button_box

    #####
    # Widget Actions
    #####

    def on_projects_btn_pressed(self):
        """
        Called when the projects button is pressed. Is also called after some project information edits.
        """

        # Check to see if any other sections windows are open
        if 'collections_window' in self.open_windows:
            self.close_collections_window()
            if self.collections_btn.isChecked():
                self.collections_btn.toggle()

        if 'new_collection_window' in self.open_windows:
            self.close_new_collection_window()
            if self.collections_btn.isChecked():
                self.collections_btn.toggle()

        if 'local_data_window' in self.open_windows:
            self.close_local_data_window()
            if self.localdata_btn.isChecked():
                self.localdata_btn.toggle()

        # Check to see if the projects window is already open
        if 'projects_window' in self.open_windows:
            self.close_projects_window()

        # Check to see if the create new project window is open
        elif 'new_project_window' in self.open_windows:
            self.close_new_projects_window()

        # If no projects windows are open then create a projects window and show
        elif 'projects_window' not in self.open_windows and 'new_project_window' not in self.open_windows:
            self.open_windows.add('projects_window')
            self.parent.projects_window = ProjectsWindow(self.app, self.token, self.parent)
            self.parent.mdi.addSubWindow(self.parent.projects_window)
            self.parent.projects_window.show()

    def on_collections_btn_pressed(self):
        """
        Called when the collections button is pressed. Is also called by child windows to re-initialise after edits.
        Returns:
            None
        """
        # Check to see if any other sections windows are open
        if 'local_data_window' in self.open_windows:
            self.close_local_data_window()
            if self.localdata_btn.isChecked():
                self.localdata_btn.toggle()

        if 'projects_window' in self.open_windows:
            self.close_projects_window()
            if self.projects_btn.isChecked():
                self.projects_btn.toggle()
        if 'new_project_window' in self.open_windows:
            self.close_new_projects_window()
            if self.projects_btn.isChecked():
                self.projects_btn.toggle()

        # check to see if the collections window is already open
        if 'collections_window' in self.open_windows:
            self.close_collections_window()
        elif 'new_collection_window' in self.open_windows:
            self.close_new_collection_window()

        # If no collections windows are open then create the collections window and show
        elif 'collections_window' not in self.open_windows and 'new_collection_window' not in self.open_windows:
            self.open_windows.add('collections_window')
            self.parent.collections_window = CollectionsWindow(self.app, self.token, self.parent)
            self.parent.mdi.addSubWindow(self.parent.collections_window)
            self.parent.collections_window.show()

    def on_local_data_btn_pressed(self):
        """
        Called when the local data button is pressed.
        :return:
        """

        # Check to see if any other sections windows are open
        if 'projects_window' in self.open_windows:
            self.close_projects_window()
            if self.projects_btn.isChecked():
                self.projects_btn.toggle()
        if 'new_project_window' in self.open_windows:
            self.close_new_projects_window()
            if self.projects_btn.isChecked():
                self.projects_btn.toggle()

        if 'collections_window' in self.open_windows:
            self.close_collections_window()
            if self.collections_btn.isChecked():
                self.collections_btn.toggle()
        if 'new_collection_window' in self.open_windows:
            self.close_new_collection_window()
            if self.collections_btn.isChecked():
                self.collections_btn.toggle()

        # Check to see if window is already open
        if 'local_data_window' in self.open_windows:
            self.close_local_data_window()

        else:
            self.open_windows.add('local_data_window')
            self.parent.local_data_window = DataWindow(self.app, self.token, self.parent)
            self.parent.mdi.addSubWindow(self.parent.local_data_window)
            self.parent.local_data_window.show()

            self.open_windows.add('data_articles_window')
            self.parent.data_articles_window = DataArticlesWindow(self.app, self.token, self.parent)
            self.parent.mdi.addSubWindow(self.parent.data_articles_window)
            self.parent.data_articles_window.show()

            self.open_windows.add('figshare_add_window')
            self.parent.figshare_add_window = FigshareAddWindow(self.app, self.token, self.parent)
            self.parent.mdi.addSubWindow(self.parent.figshare_add_window)
            self.parent.figshare_add_window.show()

    def close_projects_window(self):
        """
        Called to close the proejcts window and any children
        :return:
        """

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

        # Check to see if the article edit window is open
        if 'article_edit_window' in self.open_windows:
            self.open_windows.remove('article_edit_window')
            self.parent.article_edit_window.close()

    def close_new_projects_window(self):
        """
        Called to close the new projects window
        :return:
        """
        self.open_windows.remove('new_project_window')
        self.parent.new_project_window.close()

    def close_collections_window(self):
        """
        Called to close the collections window and any children

        Returns:
            None
        """
        self.open_windows.remove('collections_window')
        self.parent.collections_window.close()

        # Check to see if a collections info window is open
        if 'collection_info_window' in self.open_windows:
            self.open_windows.remove('collection_info_window')
            self.parent.collection_info_window.close()

        # Check to see if a collection articles window is open
        if 'collection_articles_window' in self.open_windows:
            self.open_windows.remove('collection_articles_window')
            self.parent.collection_articles_window.close()

        # Check to see if a collection article edit window is open
        if 'article_edit_window' in self.open_windows:
            self.open_windows.remove('article_edit_window')
            self.parent.article_edit_window.close()

    def close_new_collection_window(self):
        """
        Called to close the new collections window

        Returns:
            None
        """
        self.open_windows.remove('new_collection_window')
        self.parent.new_collection_window.close()

    def close_local_data_window(self):

        self.open_windows.remove('local_data_window')
        self.parent.local_data_window.close()

        self.open_windows.remove('data_articles_window')
        self.parent.data_articles_window.close()

        self.open_windows.remove('figshare_add_window')
        self.parent.figshare_add_window.close()

    def open_data_articles_window(self):
        """
        Can be called from child windows to open the data articles window
        :return:
        """
        self.parent.open_windows.add('data_articles_window')
        self.parent.data_articles_window = DataArticlesWindow(self.app, self.token, self.parent)
        self.parent.mdi.addSubWindow(self.parent.data_articles_window)
        self.parent.data_articles_window.show()
