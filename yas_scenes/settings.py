import json
import os


try:
    settings_file = os.environ['SCENES_SETTINGS']
except KeyError:
    raise Exception("Please set the envvar SCENES_SETTINGS to the"
                    " location of the YASARA scenes settings file")

try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except IOError:
    raise Exception("Please provide the YASARA scenes settings in {}".format(
        settings_file))
