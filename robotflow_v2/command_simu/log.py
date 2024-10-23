from cmd import log
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# import constants
from robotflow_v2.constants import LogType
from robotflow_v2.constants.LogType import *
if __name__ == '__main__':
    str = 'test'
    print(ERROR)
    log(LogType.INFO, str)
    log(LogType.ERROR, str)


