import logging
import sys

# root logger
_log = logging.getLogger()
_log.setLevel(logging.INFO)
_stream = logging.StreamHandler(sys.stdout)
_formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s ")
_stream.setFormatter(_formatter)
_log.addHandler(_stream)
