import logging
import sys

# root logger
_log = logging.getLogger()
_log.setLevel(logging.INFO)
_formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s ")
_stream = logging.StreamHandler(sys.stdout)
_stream.setFormatter(_formatter)
_log.addHandler(_stream)

# settings
from settings import settings_file
_log.info("Using settings from {}".format(settings_file))
