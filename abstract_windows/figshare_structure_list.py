"""
Figshare Strucure List

This module abstract the visualisation of Figshare structures such as Projects and Collections.
It produces a QMdiSubWindow object with custom widgets within it that view the different Figshare objects as an array of
QPushButtons. Other widgets provide Figshare object creation, and deletion functionality. In addition a search field is
provided to allow for the list to be filtered.

Notes:
    The FigshareObjectWindow Class is intended to have specific functions and variables overwritten by child classes,
    and therefore will not work correctly is called directly. Child classes should overwrite the following functions and
    variables.

    Functions:
        on_create_button_pressed()
        is_info_open()
        close_object_info_window()
        create_new_object_info_window()
        reopen_objects()
        get_object_list()
        search_objects()
        delete_object()

"""
# Standard Lib Imports
import os

# PyQt Imports
from PyQt5.QtWidgets import (QMdiSubWindow, QLabel, QPushButton, QMessageBox, QMainWindow, QApplication,
                             QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar)
from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (Qt)

# Figshare Desktop Imports
from Figshare_desktop.formatting.formatting import (scaling_ratio, checkable_button, search_bar)

# Figshare API Imports

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class FigshareObjectWindow(QMdiSubWindow):
    """
    An abstract base class for viewing high level Figshare objects.
    """

    def __init__(self, app: QApplication, OAuth_token: str, parent: QMainWindow):
        """
        Initialise the window

        Args:
            app: Main thread application object.
            OAuth_token: Users Figshare authentication token obtained at login.
            parent: Reference to the applications main window, where various variables are kept.
        """
        # Super the QMdiSubWindow init function
        super().__init__()

        # Create class variables of init args
        self.app = app
        self.token = OAuth_token
        self.parent = parent

        # Create shortned reference to open windows set in the main window
        self.open_windows = self.parent.open_windows

        # Initialise the Figshare information and UI
        self.initFig()
        self.initUI()

    def initFig(self):
        """
        Function should create a class variable with a list of the Figshare objects to be visualised.
        Should be overwritten by child classes
        Returns:
            None
        """
        self.object_list = self.get_object_list()

    def initUI(self):
        """
        Formats and shows the window.
        Returns:
            None
        """
        # Call the window formatting function
        self.format_window()

        # Create a horizontal box layout to hold the figshare object buttons
        self.object_buttons_box = QHBoxLayout()
        # Create a vertical box layout to hold the project window widgets and layouts
        self.vbox = QVBoxLayout()

        # Add the Figshare Object buttons to the vertical box layout
        init_finish = len(self.object_list)
        if init_finish > 4:
            init_finish = 4
        self.create_object_bar(0, init_finish)
        self.vbox.addLayout(self.object_buttons_box)

        # Add the scroll bar to the vertical box layout
        self.s_bar = self.scroll_bar()
        self.vbox.addWidget(self.s_bar)

        # Create an encompassing layout
        self.hbox = QHBoxLayout()

        # Create a layout for the search and managment widgets
        control_layout = QVBoxLayout()
        control_layout.addWidget(self.search_bar())
        control_layout.addLayout(self.management_buttons())

        # Add the control layout and the vertical button layout to the encompassing layout
        self.hbox.addLayout(control_layout)
        self.hbox.addLayout(self.vbox)

        # Create a central widget for the objects window
        window_widget = QWidget()
        # Add the vertical box layout
        window_widget.setLayout(self.hbox)
        # Set the projects window widget
        self.setWidget(window_widget)

    # Window Formatting
    # =================

    def format_window(self):
        """
        Formats the window based on the available space in the primary screen.
        Returns:
            None
        """
        # Gets the QRect of the main window
        geom = self.parent.geometry()
        # Gets the Qrect of the sections window
        section_geom = self.parent.section_geom

        # Define geometries for the projects window
        x0 = section_geom.x() + section_geom.width()
        y0 = section_geom.y()
        w = geom.width() - x0
        h = ((geom.height() - y0) / 6)
        self.setGeometry(x0, y0, w, h)
        # Remove frame from projects window
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Set the default tool tip time duration to 1 second
        self.tool_tip_time = 1000

    # Window Widgets
    # ==============

    def scroll_bar(self):
        """
        Creates a QScrollBar set to the size of the figshare objects list.

        Returns:
            s_bar (QScrollBar): Scroll bar used to move through the list of Figsahre objects.
        """
        s_bar = QScrollBar(Qt.Horizontal)
        s_bar.setMaximum(len(self.object_list) - 4)
        s_bar.sliderMoved.connect(self.slider_val)
        s_bar.valueChanged.connect(self.slider_val)
        return s_bar

    def create_obj_thumb(self, title: str, published_date: str, object_id: int):
        """
        Creates a large QPushButton with information on the objects title, and published date.

        Args:
            title: Name of the Figshare object.
            published_date: String representation of when/if the object was made public.
            object_id: Figshare object ID number

        Returns:
            btn (QPushButton): Button connected to open a subwindow with its specific ID number.
        """

        # Get the scaling rations for the current display
        w_ratio, f_ratio = scaling_ratio(self.app)
        # Scale the font sizes
        title_fnt_size = 12 * f_ratio
        date_ftn_size = 8 * f_ratio

        # Create the Title Label
        # Create the title label
        title_lbl = QLabel()
        title_lbl.setText("{}".format(title))
        title_lbl_fnt = QFont('SansSerif', title_fnt_size)
        title_lbl_fnt.setBold(True)
        title_lbl.setFont(title_lbl_fnt)
        title_lbl.setWordWrap(True)

        # Create the date label
        date_lbl = QLabel()
        if published_date is None:
            published_date = 'Private'
        date_lbl.setText("Published: {}".format(published_date))
        date_lbl_fnt = QFont('SansSerif', date_ftn_size)
        date_lbl.setFont(date_lbl_fnt)
        date_lbl.setStyleSheet('color: gray')
        date_lbl.setWordWrap(True)

        # Create a layout to hold the labels
        lbl_box = QVBoxLayout()
        # Add labels to layout
        lbl_box.addWidget(title_lbl)
        lbl_box.addWidget(date_lbl)

        # Create a button for the project
        btn = QPushButton(self)
        checkable_button(self.app, btn)
        btn.setLayout(lbl_box)
        btn.clicked[bool].connect(lambda: self.on_object_pressed(object_id))

        self.object_buttons_box.addWidget(btn)

    def create_object_bar(self, start: int, finish: int):
        """
        Creates a series of Object Push Buttons from a defined subset of the total list.

        Args:
            start: Starting element from the objects list.
            finish: Finishing element from the objects list.

        Returns:
            None
        """
        self.buttons = {}
        i = 0
        for object_pos in range(start, finish):
            title = self.object_list[object_pos]['title']
            pub_date = self.object_list[object_pos]['published_date']
            object_id = self.object_list[object_pos]['id']
            self.create_obj_thumb(title, pub_date, object_id)
            self.buttons[object_id] = self.object_buttons_box.itemAt(i).widget()
            i += 1

    def management_buttons(self):
        """
        Creates a QLayout object that hold the buttons used for creating and deleting Figsahre objects.

        Returns:
            hbox (QHBoxLayout): Horizontal layout with the create and delete buttons within it.
        """
        # Create New Project Button
        np_btn = QPushButton()
        np_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        np_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/Folder-48.png')))
        np_btn.setToolTip('Create a new Figshare Object')
        np_btn.setToolTipDuration(self.tool_tip_time)
        np_btn.pressed.connect(self.on_create_btn_pressed)

        # Create Delete Project Button
        del_btn = QPushButton()
        del_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        del_btn.setIcon(QIcon(os.path.abspath(__file__ + '/../..' + '/img/del_folder.png')))
        del_btn.setToolTip('Delete Selected Object')
        del_btn.setToolTipDuration(self.tool_tip_time)
        del_btn.pressed.connect(self.on_delete_btn_pressed)

        # Create layout to hold buttons
        hbox = QHBoxLayout()
        # Add Buttons to layout
        hbox.addWidget(np_btn)
        hbox.addWidget(del_btn)

        return hbox

    def search_bar(self):
        """
        Creates a QLineEdit object for the user to enter search queries that will filter the total object list.

        Returns:
            edit (QLineEdit): Edit field connected to perform a search either when return is pressed or focus is
                shifted away from the edit.
        """
        # Create text box
        edit = QLineEdit()
        # Set font style
        search_bar(self.app, edit)
        # Set place holder text
        edit.setPlaceholderText('Search')
        # Add a clear button to the line edit
        edit.setClearButtonEnabled(True)
        # Add mouse over text
        edit.setToolTip('Search for specific Figshare objects')
        edit.setToolTipDuration(self.tool_tip_time)
        # Connect search function to the return key
        edit.returnPressed.connect(lambda: self.search_on_return(edit.text()))
        edit.textChanged.connect(lambda: self.search_on_clear(edit.text()))
        return edit

    # Widget Actions
    # ==============

    def slider_val(self):
        """
        Called when the objects slider is changed. Removes all existing buttons and regenerates from the new list
        position.

        Returns:
            None
        """
        # Remove all existing button widgets
        while self.object_buttons_box.count():
            item = self.object_buttons_box.takeAt(0)
            item.widget().deleteLater()

        # Get the current value of the scroll bar
        s_bar_pos = self.s_bar.value()

        # Define how many buttons to visualise
        if 1 < len(self.object_list) < 4:
            number = len(self.object_list)
        else:
            number = 4

        self.s_bar.setMaximum(len(self.object_list) - number)  # Will be zero if less than 4 items in list
        self.create_object_bar(s_bar_pos, s_bar_pos + number)  # Recreates the button view from the new position

    def search_init(self):
        """
        Called when the object search bar is used. Removes all existing buttons anfe regenerates from the new list.

        Returns:
            None
        """
        # Remove all existing button widgets
        while self.object_buttons_box.count():
            item = self.object_buttons_box.takeAt(0)
            item.widget().deleteLater()

        # Define how many buttons to visualise
        if 1 <= len(self.object_list) <= 4:
            number = len(self.object_list)
        else:
            number = 4

        self.s_bar.setMaximum(len(self.object_list) - number)  # Will be zero if less than 4 items in list
        self.create_object_bar(0, number)  # Recreates the button view from the new position

    def search_on_return(self, search_text: str):
        """
        Called when the return key is pressed in the search bar. Will search the relavant Figshare object endpoint based
        on the query string. Will overwrite the existing objects list with that of the search result.

        Args:
            search_text: Elastic search query with which to search the object titles for.

        Returns:
            None
        """
        self.object_list = self.search_objects(search_text)  # Perform the search
        self.search_init()  # Redraw the object buttons

    def search_on_clear(self, search_text: str):
        """
        Called when the search bar is cleared, or if the focus is removed and the search string is empty

        Args:
            search_text: strign from the search LineEdit

        Returns:
            None
        """
        if search_text == '':
            self.object_list = self.get_object_list()
            self.slider_val()

    def on_create_btn_pressed(self):
        """
        Called when the create new object button is pressed.

        MUST BE OVERWRITTEN BY CHILDREN.

        Examples:
            Example of code is given where '' denotes the sections that should be manually defined to the specific
            figshare object being used.

                if new_''_window in self.open_Windows:
                    self.open_windows.remove(new_''_window)
                    self.parent.new_''_window.close()
                else:
                    self.open_windows.remove(''_window)
                    self.close()
                    self.open_windows.add('new_''_window)
                    self.parent.new_''_window = New''Window(self.app, self.token, self.parent)
                    self.parent.mdi.addSubWindow(self.parent.new_''_window)
                    self.parent.new_''_window.show()

        Returns:
            None
        """
        pass

    def is_info_open(self):
        """
        Called to see if there is a Figshare object info window open.

        MUST BE OVERWRITTEN BY CHILDREN.

        Examples:
               Example of code is given where '' denotes the sections that should be manually defined to the specific
               figshare object being used.

               if ''_info_window in self.open_windows:
                    open_obj_id = self.parent.''_info_window.''_id
                    return True, open_obj_id
                else:
                    return False, None

        Returns:
            open (bool): True, or False dependent on if info window is already open
            object_id (int): Figshare object ID number
        """
        pass

    def close_object_info_window(self):
        """
        Called when the existing object info window needs to be closed.

        MUST BE OVERWRITTEN BY CHIDREN.
        Examples:
            Example of code is given where '' denotes the sections that should be manually defined to the specifc
            figshare object being used.

            self.open_windows.remove("''_info_window")
            self.parent.''_info_window.close()

            if ''_articles_window in self.open_windows:
                self.open_windows.remove("''_articles_window")
                self.parent.''_articles_window.close()
            if 'article_edit_window' in self.open_windows:
                self.open_windows.remove('article_edit_window')
                self.parent.article_edit_window.close()

        Returns:
            None
        """

    def create_new_object_info_window(self, object_id: int):
        """
        Called when a new object info window is to be created.

        MUST BE OVERWRITTEN BY CHILDREN.

        Examples:
            Example of code is given where '' denotes the sections that should be manually defined to the specific
            figshare object being used.

            self.open_windows.add("''_info_window")
            self.parent.''_info_window = ''InfoWindow(self.app, self.token, self.parent, self.object_id)
            self.parent.mdi.addSubWindow(self.parent.''_info_window)
            self.parent.''_info_window.show()

        Args:
            object_id: Figshare object ID number.

        Returns:
            None
        """
        pass

    def on_object_pressed(self, object_id: int):
        """
        Called when an object button is clicked. If an object info window is already open will see if it is the same
        as the object just pressed. If it is, then it is closed. If it is not the same then the currently open info
        window is closed and the new object window is opened in its place.

        Args:
            object_id: Figshare object ID number.

        Returns:
            None
        """
        # Check to see if an object window is open
        info_open, open_obj_id = self.is_info_open()

        if info_open:
            # Check to see if the open object is the same as the object that was just pressed
            if open_obj_id != object_id:
                # Check to see if we need to toggle a button by seeing if the object button still exists.
                # It may have been scrolled away from.
                if open_obj_id in self.buttons:
                    # Finally check that it is checked, and un-check it if so.
                    if self.buttons[open_obj_id].isChecked():
                        self.buttons[open_obj_id].toggle()
                # Close the currently open info window
                self.close_object_info_window()
                # Create and open new object info window
                self.create_new_object_info_window(object_id)

            # If the button pressed corresponds to the existing object
            else:
                # Close the object info window
                self.close_object_info_window()

        else:
            self.create_new_object_info_window(object_id)

    def on_delete_btn_pressed(self):
        """
        Called when the object delete button is pressed.

        Returns:
            None
        """
        # See if an info window is open, and get its object ID number if so
        info_open, open_obj_id = self.is_info_open()

        if info_open:

            # Create a confirmation dialog
            msg = "Are you sure you want to delete the open Figshare Object?"
            msg_box = QMessageBox.question(self, "Deletion Confirmation", msg, QMessageBox.Yes, QMessageBox.No)

            if msg_box == QMessageBox.Yes:
                # Attempt to delete the Figshare object
                successful = self.delete_object(open_obj_id)

                if successful:
                    con_reply = QMessageBox.information(self, "Deletion Confirmation", "Object successfully deleted.",
                                                        QMessageBox.Ok)
                    if con_reply is not None:
                        self.reopen_objects()
                else:
                    con_reply = QMessageBox.warning(self, "Deletion Confirmation", "Object could not be deleted",
                                                    QMessageBox.Ok)

                    if con_reply is not None:
                        self.reopen_objects()

    def reopen_objects(self):
        """
        Called to open and close the figshare objects window

        MUST BE OVERWRITTEN BY CHILDREN.

        Examples:
            Example of code is given where '' denotes the sections that should be manually defined to the specific
            figshare object being used.

            for i in range(2):
            self.parent.section_window.on_''_btn_pressed()

        Returns:
            None
        """

    # Figshare API Interface Functions
    # ================================

    def get_object_list(self):
        """
        Called to return a list of Figshare object associated to the user.

        MUST BE OVERWRITTEN BY CHILDREN.

        Examples:
            Example of code is given where '' denotes the sections that should be manually defined to the specific
            figshare object being used.

            '' = ''(self.token)
            object_list = ''.get_list()
            return object_list

        Returns:
            object_list (list of dicts): List of users Figshare objects.
        """
        pass

    def search_objects(self, search_text: str):
        """
        Gets a list of objects matching the users search query.

        MUST BE OVERWRITTEN BY CHILDREN.

        Examples:
            Example of code is given where '' denotes the sections that should be manually defined to the specific
            figshare object being used.

            '' = ''(self.token)
            result = ''.search(search_text)
            if len(result) == 0:
            result = ''.get_list()

            return result

        Args:
            search_text: Figshare style elastic search string

        Returns:
            result (list of dicts): Gives a list of dictionary objects that either match those of the search criteria,
                or returns the full set if no matches found.
        """
        pass

    def delete_object(self, object_id: int):
        """
        Called to delete the given figshare object.

        MUST BE OVERWRITTEN BY CHILDREN.

        Examples:
            Example of code is given where '' denotes the sections that should be manually defined to the specific
            figshare object being used.

            '' = ''(self.token)
            try:
                ''.delete(object_id, safe=False)  # Suppresses command line requirement for confirmation
                return True
            except:
                return False

        Args:
            object_id:

        Returns:
            bool: True of False dependent on if the deletion was successful.
        """
