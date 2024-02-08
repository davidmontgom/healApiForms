__all__ = ["logging", "PROJECT_ROOT"]
import logging
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# from error_tools import log_error

#####################################################################
# SETUP LOGGING
#####################################################################
logging.getLogger(__name__).addHandler(logging.NullHandler())
# logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(name)-12s [%(levelname)s] [%(filename)s:%(lineno)d in function "
    "%(funcName)s] %(message)s",
    handlers=[
        # logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ],
)
