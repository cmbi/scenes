from __future__ import absolute_import

import logging

_log = logging.getLogger(__name__)

import re

from yas_scenes.scenes import (create_ion_scene, create_sym_scene, exit_yasara,
                               prepare_yasara)


def ion_sites(pdb_file_path, yasara_scene_path, ion_ligand_dict,
              yasara_pid, yasara_log):
    """Creates a YASARA scene displaying ion sites.

    Create a WHY_NOT file if the scene cannot be created.
    """
    success = False
    prepare_yasara(pid=yasara_pid, yasara_log=yasara_log)
    create_ion_scene(pdb_path=pdb_file_path, sce_path=yasara_scene_path,
                     ion_sites=ion_ligand_dict)
    success = exit_yasara()
    if success:
        return has_logged_exit(yasara_log)
    return success


def symmetry_contacts(pdb_file_path, yasara_scene_path, symmetry_contacts_dict,
                      yasara_pid, yasara_log):
    """Creates a YASARA scene displaying symmetry contacts.

    Return a boolean indicating whether everything went succesful
    Return also a string reporting the most important reason why things went
        ok or went wrong.
    """
    success = False
    try:
        # Set pid and open a log file
        prepare_yasara(pid=yasara_pid, yasara_log=yasara_log)
        # Create and save the scene
        create_sym_scene(pdb_path=pdb_file_path, sce_path=yasara_scene_path,
                         sym_contacts=symmetry_contacts_dict)
        msg = 'Scene created'
        success = True
        _log.debug('msg: {}'.format(yasara_scene_path))
    except Exception as e:
        # The scene will not be created if an exception is raised
        _log.debug(e)
        _log.error('Scene {} could not be created!'.format(yasara_scene_path))
        msg = 'Error creating YASARA scene'
        return False, msg
    finally:
        # Exit and close log
        exit = exit_yasara()

    if not exit:
        msg = 'Error terminating YASARA'
        return False, msg

    has_exit, num_lines = has_logged_exit(yasara_log)
    if not has_exit:
        msg = 'Error terminating YASARA: no Exit statement in YASARA log'
        return False, msg

    if not has_expected_log_count_symm(num_lines, symmetry_contacts_dict):
        msg = 'Error creating YASARA scene: some commands could not be executed'
        return False, msg

    return success, msg


def has_expected_log_count_symm(found_log_lines, symmetry_contacts):
    """Returns True if the number of found log lines equals the expected number.

    The expected number of logs is calculated as follows (pseudocode):
        +5 (newline, set CPU number, load PDB, set style, color all)
        loop over all residues:
            +3 if num_contacts > 0 else +2
        +6 (color background, stick, ballstick, niceoriall, savesce, exit)
    """
    head = 5
    tail = 6
    res = 0
    for n in symmetry_contacts.itervalues():
        if n > 0:
            res = res + 3
        else:
            res = res + 2
    expected = head + res + tail

    if not found_log_lines == expected:
        _log.error('Number of log lines ({}) not equal to expected number of '
                   'log lines ({})'.format(found_log_lines, expected))
    else:
        _log.debug('Number of log lines ({}) equal to expected number of '
                   'log lines ({})'.format(found_log_lines, expected))

    return found_log_lines == expected


def has_logged_exit(yasara_log):
    """Checks if the last line of the yasara_log is the Exit command.

    Return True if the last line is the Exit command.
    Also return the number of lines in the file up to the end."""
    exit_present = False
    num_lines = 0
    try:
        with open(yasara_log + '.log', 'r') as f:
            for last_line in f:
                num_lines = num_lines + 1
            _log.debug('{} has {} lines'.format(yasara_log, num_lines))
            if re.match('^>Exit$', last_line):
                _log.debug('Exit found in last line of {}'.format(yasara_log))
                exit_present = True
    except IOError as e:
        _log.error(e)

    return exit_present, num_lines
