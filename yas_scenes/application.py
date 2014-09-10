import logging
_log = logging.getLogger(__name__)

import argparse

from yas_scenes.parser import parse_ion_sites, parse_sym_contacts
from yas_scenes.tasks import ion_sites, symmetry_contacts
from yas_scenes.utils import (delete_scene, is_valid_file, is_valid_pdbid,
                              set_dir_log_wn, write_whynot)


def ion(args):
    """Create ion site YASARA scene

    This function wil create in SCENES_ROOT/iod/pdbid
    - either a YASARA scene or a WHY_NOT file
    - the YASARA log
    - this program's log

    SCENES_ROOT is configured in scenes_settings
    pdbid is a command line argument

    SCENES_NAME is configured in scenes_settings
    and determines file names and WHY_NOT database name
    """
    scene_path, yas_log_path, wn_file, wn_db = set_dir_log_wn(args, 'iod')
    ion_ligands = parse_ion_sites(iod=args.iod)

    _log.info('Will try to create ion sites YASARA scene {} from {} '
              'and {} for PDB ID {}'.format(scene_path, args.pdb_file_path,
                                            args.iod, args.pdb_id))
    success, msg = ion_sites(args.pdb_file_path, scene_path,
                             ion_ligands, args.ypid, yas_log_path)

    if not success:
        _log.error('{}: {}'.format(args.pdb_id, msg))
        # If the scene file is still present, delete it
        delete_scene(scene_path)
        # Create a WHY NOT entry
        write_whynot(args.pdb_id, msg, wn_db, wn_file)
    else:
        _log.info('{}: {}'.format(args.pdb_id, msg))


def ss2(args):
    """Create symmetry contacts YASARA scene

    This function wil create in SCENES_ROOT/ss2/pdbid
    - either a YASARA scene or a WHY_NOT file
    - the YASARA log
    - this program's log

    SCENES_ROOT is configured in scenes_settings
    pdbid is a command line argument

    SCENES_NAME is configured in scenes_settings
    and determines file names and WHY_NOT database name
    """
    scene_path, yas_log_path, wn_file, wn_db = set_dir_log_wn(args, 'ss2')
    sym_contacts = parse_sym_contacts(ss2=args.ss2)

    _log.info('Will try to create symmetry contacts YASARA scene {} from {} '
              'and {} for PDB ID {}'.format(scene_path, args.pdb_file_path,
                                            args.ss2, args.pdb_id))
    success, msg = symmetry_contacts(args.pdb_file_path, scene_path,
                                     sym_contacts, args.ypid, yas_log_path)

    if not success:
        _log.error('{}: {}'.format(args.pdb_id, msg))
        # If the scene file is still present, delete it
        delete_scene(scene_path)
        # Create a WHY NOT entry
        write_whynot(args.pdb_id, msg, wn_db, wn_file)
    else:
        _log.info('{}: {}'.format(args.pdb_id, msg))


def main():
    """Create YASARA scenes."""

    parser = argparse.ArgumentParser(description="Create a YASARA scene.",
                                     prog="scenes")
    parser.add_argument("-v", "--verbose", help="show verbose output",
                        action="store_true")
    parser.add_argument("ypid", help="YASARA process id. Warning: specify a "
                        "different pid if multiple YASARA instances run on the"
                        " same machine", type=int)
    parser.add_argument("pdb_file_path", help="PDB file location.",
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument("pdb_id", help="PDB accession code.",
                        type=lambda x: is_valid_pdbid(parser, x))
    parser.add_argument("source", choices=["PDB", "REDO"],
                        help="PDB file source")
    subparsers = parser.add_subparsers(title="mode",
                                       description="YASARA scene type",
                                       help="ion for ion sites, symm for "
                                            "symmetry contacts")
    p_ion = subparsers.add_parser("ion", description="Create a YASARA scene of"
                                  " ion sites")
    p_ion.add_argument("iod", help="WHAT IF list iod file (bzip2ed)",
                       type=lambda x: is_valid_file(parser, x))
    p_ion.set_defaults(func=ion)
    p_ss2 = subparsers.add_parser("symm", description="Create a YASARA scene"
                                  " with colored symmetry contacts")
    p_ss2.add_argument("ss2", help="WHAT IF list symmetry contacts file "
                                   "(bzip2ed), e.g. 1crn.ss2.bz2",
                       type=lambda x: is_valid_file(parser, x))
    p_ss2.set_defaults(func=ss2)

    args = parser.parse_args()

    args.func(args)
