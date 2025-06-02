from enum import Enum
import sys, os


MAIN_FILE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
ASSETS_SUBDIR = "assets"
PAGES_SUBDIR = "pages"

class PathVariable(Enum):
    NOTEBOOK_PATH = os.path.join(MAIN_FILE_PATH, ASSETS_SUBDIR, "notebook")
    SAVE_PATH =     os.path.join(MAIN_FILE_PATH, ASSETS_SUBDIR, "save")
    TEMPLATE_PATH = os.path.join(MAIN_FILE_PATH, ASSETS_SUBDIR, "template")
    TMP_PATH =      os.path.join(MAIN_FILE_PATH, ASSETS_SUBDIR, "tmp")
    PAGES_PATH =    os.path.join(MAIN_FILE_PATH, PAGES_SUBDIR)
