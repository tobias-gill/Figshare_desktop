"""

"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QProgressBar, QAbstractItemView, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtGui import (QFont, QColor, QPainter)
from PyQt5.QtCore import (Qt, QRect)

from Figshare_desktop.figshare_articles.determine_type import gen_article
from Figshare_desktop.custom_widgets.progress_bar import ArticleLoadBar
from figshare_interface import Projects

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class ArticleList(QWidget):

    def __init__(self, OAuth_token, project_id, parent):
        super().__init__()

        self.token = OAuth_token
        self.project_id = project_id
        self.parent = parent

        self.initFig()
        self.initUI()

    def initFig(self):
        """
        Initial data load from Figshare
        :return:
        """
        # Get the list of articles from
        projects = Projects(self.token)
        articles = projects.list_articles(self.project_id)
        n_articles = len(articles)
        # Create progress bar
        bar = ArticleLoadBar(n_articles, self.parent)

        # Create Local Versions of articles
        step = 0
        for article in articles:
            self.create_local_article(article)
            bar.update_progress(step)
            step += 1

    def initUI(self):

        vbox = QVBoxLayout()
        vbox.addWidget(self.initTree())
        # Set Widget layout
        self.setLayout(vbox)

    def initTree(self):
        """
        Called to initilize the QTree widget
        :return:
        """

        # Create instance of QTreeWidget
        tree = QTreeWidget()
        # Format tree to allow for multiple items to be selected
        tree.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Create the initial set of column headers
        headers = ['title', 'id', 'created_date', 'up_to_date', 'type', 'tags']
        header_item = QTreeWidgetItem(headers)
        tree.setHeaderItem(header_item)

        return tree

    #####
    # Figshare Article Functions
    #####

    def does_article_exist_locally(self, article_id):
        """
        Checks to see if there is a local version of the article.
        :param article_id: int. Figshare article id number
        :return: Bool. Dependent on if local version of article exists or not
        """

        # Convert article id to a string. Should have already been done, but just in case we call it somewhere else
        a_id = str(article_id)

        if a_id in self.parent.figshare_articles:
            return True
        else:
            return False

    def create_local_article(self, figshare_article):
        """
        Given a Figshare article id number this function will create a local version if one does not already exist
        :param figshare_article: Dict. Figshare article returned from Projects.list_articles()
        :return:
        """
        # Get the article id number and title
        article_id = str(figshare_article['id'])  # Convert int to str
        article_title = figshare_article['title']

        # If article is not already stored locally create a
        if not self.does_article_exist_locally(article_id):
            article = gen_article(article_title, self.token, self.project_id, article_id)
            self.parent.figshare_articles[article_id] = article

    def progress_bar(self, n_articles):
        """
        Called to indicate the progress of creating local version of figshare articles
        :param n_articles:
        :return:
        """

        pbar = QProgressBar()
        pbar.setMaximum(n_articles - 1)

        return pbar
