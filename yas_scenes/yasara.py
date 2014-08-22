# **********************************************************
# *                                                        *
# *                    Y  A  S  A  R  A                    *
# *                                                        *
# * Yet Another Scientific Artificial Reality Application  *
# *                                                        *
# **********************************************************
# *  yasara.py - The loader for the YASARA Python module   *
# * You can find the complete documentation of this module *
# *    in YASARA's HTML manual yasara/doc/index.html at    *
# *       'Scripts - Use YASARA as a Python module'.       *
# *      To get a list of all defined functions, type      *
# *                 help('yasaramodule')                   *
# *          License for this Python module: BSD           *
# **********************************************************

# IMPORTANT: Copy this module to a place where Python can find
# it, e.g. the directory where you keep your own Python modules.
# If you move YASARA somewhere else, please adapt the path below:

import os
import sys
import pyconfig

yasara_dir = pyconfig.get('YASARA_DIR')
sys.path.append(os.path.join(yasara_dir, 'pym'))
sys.path.append(os.path.join(yasara_dir, 'plg'))

from yasaramodule import *
