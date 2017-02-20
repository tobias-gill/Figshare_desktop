"""

"""

from os.path import splitext

from .article import Article
from .stm_articles.spectroscopy_article import SpecArticle
from .stm_articles.topography_article import TopoArticle

from ..local_articles.local_article import LocalArticle

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


def gen_article(filename, OAuth_token, project_id, article_id):

    file_path, file_ext = splitext(filename)

    file_types = {
                  # OMICRON FLAT FILES
                  '.Z_flat': TopoArticle,
                  '.I(V)_flat': SpecArticle,
                  '.Aux1(V)_flat': SpecArticle,
                  '.Aux2(V)_flat': SpecArticle,

                  # ZYVEX Files
                  '.zad': TopoArticle
                  }

    if file_ext in file_types:
        return file_types[file_ext](OAuth_token, project_id, article_id)
    else:
        return Article(OAuth_token, project_id, article_id)


def gen_local_article(filename):
    file_path, file_ext = splitext(filename)

    file_types = {}

    if file_ext in file_types:
        return file_types[file_ext]()
    else:
        return LocalArticle(filename)