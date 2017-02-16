"""
"""

import os
import sys
from time import sleep
from PyQt5.QtCore import (QCoreApplication, Qt, QPoint)
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton)
from PyQt5.QtGui import (QPixmap, QFont)

from figshare_interface.http_requests.figshare_requests import login_request

from Figshare_desktop.main_window.main_window import MainWindow

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignCenter)

        self.label_font = QFont('SansSerif', 10)
        self.edit_font = QFont('SansSerif', 8)
        self.button_font = QFont('SansSerif', 10)

        self.placeLogo()
        self.placeAccountNameLabel()
        self.placeAccountNameEdit()
        self.placePasswordLabel()
        self.placePasswordEdit()
        self.placeQuitButton()
        self.placeLoginButton()

        self.setLayout(self.grid)

        self.formatWindow()

        self.accountNameEdit.setFocus()

    def formatWindow(self):
        screen = app.primaryScreen()
        screen_rec = screen.availableGeometry()
        screen_center = screen_rec.center()
        frame_w = screen_rec.width() / 4
        frame_h = screen_rec.height() / 4
        self.setGeometry(screen_center.x() - frame_w / 2, screen_center.y() - frame_h / 2
                         , frame_w, frame_h)

        self.setWindowFlags(Qt.FramelessWindowHint)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def placeLogo(self):
        logo_img = QPixmap(os.path.abspath(__file__ + '/../..' + '/img/full-logo.png'))
        logo = QLabel()
        logo.setPixmap(logo_img)
        logo.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(logo, 1, 0, 5 , 1)

    def placeAccountNameLabel(self):
        accountName = QLabel('Account')
        accountName.setFont(self.label_font)
        self.grid.addWidget(accountName, 1, 1, 1, 2)

    def placeAccountNameEdit(self):
        accountNameEdit = QLineEdit()
        accountNameEdit.setFont(self.edit_font)

        accountNameEdit.returnPressed.connect(self.on_pushLogin_clicked)
        self.accountNameEdit = accountNameEdit
        self.grid.addWidget(self.accountNameEdit, 2, 1, 1, 2)


    def placePasswordLabel(self):
        passwordLabel = QLabel('Password')
        passwordLabel.setFont(self.label_font)
        self.grid.addWidget(passwordLabel, 3, 1, 1, 2)

    def placePasswordEdit(self):
        self.passwordEdit = QLineEdit()
        self.passwordEdit.setFont(self.edit_font)
        self.passwordEdit.setEchoMode(QLineEdit.Password)

        self.passwordEdit.returnPressed.connect(self.on_pushLogin_clicked)

        self.grid.addWidget(self.passwordEdit, 4, 1, 1, 2)

    def placeQuitButton(self):
        quit_btn = QPushButton('Exit', self)
        quit_btn.setFont(self.button_font)
        quit_btn.clicked.connect(QCoreApplication.instance().quit)
        quit_btn.resize(quit_btn.sizeHint())
        self.grid.addWidget(quit_btn, 5, 1)

    def placeLoginButton(self):
        login_btn = QPushButton('Login', self)
        login_btn.setFont(self.button_font)
        login_btn.clicked.connect(self.on_pushLogin_clicked)
        login_btn.resize(login_btn.sizeHint())
        self.grid.addWidget(login_btn, 5, 2)

    def on_pushLogin_clicked(self):

        username = self.accountNameEdit.text()
        password = self.passwordEdit.text()

        try:
            OAuth_token = login_request(username, password)
            self.close()
            self.window = MainWindow(app, OAuth_token)
            self.window.show()
        except:
            self.accountNameEdit.setText("")
            self.passwordEdit.setText("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec_())
