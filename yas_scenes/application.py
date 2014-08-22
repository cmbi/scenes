import logging
_log = logging.getLogger(__name__)

import argparse
import errno
import re
import os

from yas_scenes.parser import parse_sym_contacts
from yas_scenes.tasks import ion_sites, symmetry_contacts


PDB_ID_PAT = re.compile(r"^[0-9a-zA-Z]{4}$")


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


def ion(args):
    """Create ion site YASARA scene

    Example:
    pdb = 'path/to/pdb/pdb2fe8.ent'
    scene = 'sce/2fe8_ion_sites.sce'
    ions_ligands = {'Zn res 316 mol A': '190 193 225 227 mol A',
                    'Zn res 316 mol B': '190 193 225 227 mol B',
                    'Zn res 316 mol C': '190 193 225 227 mol C'}
    log = 'logs/2fe8_ion_sites'
    created = ion_sites(pdb, scene, ions_ligands, 123, log)
    if created:
        _log.info('Scene created: {}'.format(scene))
    """
    # TODO implement


def set_debug_loggers():
    # root logger
    logging.getLogger().setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s "
                                  "[in %(pathname)s:%(lineno)d]")
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)
    _log.debug('Set verbose logging')


def ss2(args):
    """Create symmetry contacts YASARA scene

    Example:
    pdb = '/path/to/pdb/pdb1crn.ent'
    scene = 'sce/1crn_sym_contacts.sce'
    sym_contacts = {'15 mol A': 1,
                    '16 mol A': 1,
                    '19 mol A': 2,
                    '21 mol A': 1,
                    '22 mol A': 1,
                    '25 mol A': 2,
                    '28 mol A': 1,
                    '36 mol A': 5,
                    '35 mol A': 7,
                    '29 mol A': 3}
    log = 'logs/1crn_sym_contacts'
    symmetry_contacts(pdb, scene, sym_contacts, 123, log)
    """
    # TODO modify as soon as we know desired directory structure
    scene = 'sce/{}_sym_contacts.sce'.format(args.pdb_id)
    sym_contacts = parse_sym_contacts(ss2=args.ss2)
    # TODO modify as soon as we know desired directory structure
    log = 'logs/{}_sym_contacts'.format(args.pdb_id)
    _log.info('Will try to create symmetry contacts YASARA scene {} from {} and'
              ' {} for PDB ID {}'.format(scene, args.pdb_file_path, args.ss2,
                                         args.pdb_id))
    success, msg = symmetry_contacts(args.pdb_file_path, scene, sym_contacts,
                                     args.ypid, log)
    if not success:
        _log.error('{}: {}'.format(args.pdb_id, msg))
        # If the scene file is still present, delete it
        delete_scene(scene)
        # Create a WHY NOT entry
        # TODO modify as soon as we know the DB name
        file_path = 'sce/{}_sym_contacts.whynot'.format(args.pdb_id)
        write_whynot(args.pdb_id, msg, 'SCENE_SYMM_CON', file_path)
    else:
        _log.info('{}: {}'.format(args.pdb_id, msg))


def write_whynot(pdb_id, reason, db, why_not_file_path=None):
    """Create a WHY NOT file.

    Return a Boolean.
    """
    if not why_not_file_path:
        why_not_file_path = '{}.whynot'.format(pdb_id)

    _log.warn('Writing WHY NOT entry.')
    try:
        with open(why_not_file_path, 'w') as whynot:
            whynot.write('COMMENT: {}\n{},{}\n'.format(reason, db.upper(),
                                                       pdb_id))
            return True
    except IOError as ex:
        _log.error(ex)
        return False


def main():
    """Create YASARA scenes."""

    parser = argparse.ArgumentParser(
        description="Create a YASARA scene. TO BE ADDED.")
    parser.add_argument("-v", "--verbose", help="show verbose output",
                        action="store_true")
    parser.add_argument("ypid", help="YASARA process id. Warning: specify a "
                        "different pid if multiple YASARA instances run on the"
                        "same machine", type=int)
    parser.add_argument("pdb_file_path", help="PDB file location.",
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument("pdb_id", help="PDB accession code.",
                        type=lambda x: is_valid_pdbid(parser, x))
    subparsers = parser.add_subparsers(title="mode",
                                       description="YASARA scene type",
                                       help="ion for ion sites, symm for "
                                            "symmetry contacts")
    p_ion = subparsers.add_parser("ion", description="Create a YASARA scene of "
                                  "ion sites")
    p_ion.add_argument("ion", help="WHAT IF list ion file (bzip2ed)",
                       type=lambda x: is_valid_file(parser, x))
    p_ion.set_defaults(func=ion)
    p_ss2 = subparsers.add_parser("symm", description="Create a YASARA scene "
                                  "with colored symmetry contacts")
    p_ss2.add_argument("ss2", help="WHAT IF list symmetry contacts file "
                                   "(bzip2ed), e.g. 1crn.ss2.bz2",
                       type=lambda x: is_valid_file(parser, x))
    p_ss2.set_defaults(func=ss2)
    args = parser.parse_args()

    if args.verbose:
        set_debug_loggers()

    args.func(args)