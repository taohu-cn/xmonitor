# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

import sys
import os

# xclient 所在目录
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
sys.path.append(BASE_DIR)

if True:
    from xclient.core import main

if __name__ == "__main__":
    import logging

    try:
        client = main.Handler(sys.argv)
    except Exception as e:
        logging.exception(e)
