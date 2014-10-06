import logging
_log = logging.getLogger(__name__)

import errno
import os
import re

from yas_scenes.settings import settings


PDB_ID_PAT = re.compile(r"^[0-9a-zA-Z]{4}$")


def create_file_logger(log_path):
    """Create a log file."""
    # root logger
    _root = logging.getLogger()
    _file = logging.FileHandler(log_path, 'w')
    _root.addHandler(_file)


def delete_scene(scene_path):
    """Delete this scene if it is present.

    Return True if the scene was present
    Raise OSError if the <present> file could not be deleted
    """
    try:
        os.remove(scene_path)
        _log.debug('Deleted {}'.format(scene_path))
        return True
    except OSError as e:
        if e.errno != errno.ENOENT:
            _log.error('Could not delete {}: {}'.format(scene_path, e))
            raise
        else:
            False


def ensure_dir_existence(scene_dir):
    """Create scene_dir if it does not exists.

    Raise an OSError if the dir could not be created or is not writable, etc.
    """
    try:
        os.makedirs(scene_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def is_valid_file(parser, arg):
    """Check if file exists and is not empty."""
    if not os.path.isfile(arg):
        parser.error('The file {} does not exist!'.format(arg))
    elif not os.stat(arg).st_size > 0:
        parser.error('The file {} is empty!'.format(arg))
    else:
        # File exists and is not empty so return the filename
        return arg


def is_valid_pdbid(parser, arg):
    """Check if this is a valid PDB identifier (anno 2014)."""
    if not re.search(PDB_ID_PAT, arg):
        parser.error('Not a valid PDB ID: {} !'.format(arg))
    else:
        return arg


def set_debug_loggers():
    """Set the loglevel of all loggers to DEBUG."""
    # root logger
    logging.getLogger().setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s"
                                  " [in %(pathname)s:%(lineno)d]")
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)
    _log.debug('Set verbose logging')


def set_dir_log_wn(args, mode):
    """Scene dir, scene path, log, verbose log, yasara log, why_not.

    Return scene path and yasara log, why_not path and db

    Raise an OSError if the dir could not be created or is not writable, etc.
    """
    if args.source == 'PDB':
        scene_dir = os.path.join(settings['PDB_SCENES_ROOT'],
                                 mode, args.pdb_id)
    elif args.source == 'REDO':
        scene_dir = os.path.join(settings['REDO_SCENES_ROOT'],
                                 mode, args.pdb_id)
    ensure_dir_existence(scene_dir)
    scene_name = settings['SCENES_NAME']
    scene_nam = scene_name[mode][0]
    scene = '{}_{}.sce'.format(args.pdb_id, scene_nam)
    scene_path = os.path.join(scene_dir, scene)

    log = 'scenes_{}_{}.log'.format(args.pdb_id, scene_nam)
    log_path = os.path.join(scene_dir, log)
    create_file_logger(log_path)
    if args.verbose:
        set_debug_loggers()

    yas_log = '{}_{}'.format(args.pdb_id, scene_nam)
    yas_log_path = os.path.join(scene_dir, yas_log)

    wn_file_path = os.path.join(scene_dir, '{}_{}.whynot'.format(
        args.pdb_id, scene_nam))
    wn_db = '{}_SCENES_{}'.format(args.source, scene_name[mode][1])

    return scene_path, yas_log_path, wn_file_path, wn_db


def write_whynot(pdb_id, reason, db, why_not_file_path=None):
    """Create a WHY NOT file.

    Return a Boolean.
    """
    if not why_not_file_path:
        why_not_file_path = '{}.whynot'.format(pdb_id)

    _log.warn('Writing WHY NOT entry.')
    try:
        with open(why_not_file_path, 'w') as whynot:
            whynot.write('COMMENT: {}\n{},{}\n'.format(reason, db, pdb_id))
            return True
    except IOError as ex:
        _log.error(ex)
        return False
