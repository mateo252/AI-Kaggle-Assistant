from enum import Enum
import sys, os



class PathVariable(Enum):
    MAIN_FILE_PATH = sys.argv[0]

    NOTEBOOK_PATH = os.path.join(MAIN_FILE_PATH, "notebook")
    SAVE_PATH =     os.path.join(MAIN_FILE_PATH, "sabe")
    TEMPLATE_PATH = os.path.join(MAIN_FILE_PATH, "template")
    TMP_PATH =      os.path.join(MAIN_FILE_PATH, "tmp")


