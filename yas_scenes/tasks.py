from __future__ import absolute_import

import logging

_log = logging.getLogger(__name__)

import re

from yas_scenes.scenes import (create_ion_scene, create_sym_scene, exit_yasara,
                               prepare_yasara)


def ion_sites(pdb_file_path, yasara_scene_path, ion_ligand_dict,
              yasara_pid, yasara_log):
    """Creates a YASARA scene displaying metal ion sites.

    Return a boolean indicating whether everything went succesful
    Return also a string reporting the most important reason why things went
        ok or went wrong.
    """
    success = False
    try:
        # Set pid and open a log file
        prepare_yasara(pid=yasara_pid, yasara_log=yasara_log)
        # Create and save the scene
        create_ion_scene(pdb_path=pdb_file_path, sce_path=yasara_scene_path,
                         ion_sites=ion_ligand_dict)
        msg = 'Scene created'
        success = True
        _log.debug('{}: {}'.format(msg, yasara_scene_path))
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

    warned, warning, warn_count = has_logged_warning(yasara_log)
    if warned:
        num_lines = num_lines - warn_count

    if not has_expected_log_count_ions(num_lines, ion_ligand_dict):
        msg = 'Error creating YASARA scene:' \
            ' some commands could not be executed correctly'
        return False, msg

    return success, msg


def symmetry_contacts(pdb_file_path, yasara_scene_path, symmetry_contacts_dict,
                      yasara_pid, yasara_log):
    """Creates a YASARA scene displaying crystal contacts.

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
        _log.debug('{}: {}'.format(msg, yasara_scene_path))
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

    warned, warning, warn_count = has_logged_warning(yasara_log)
    if warned:
        _log.error(warn_count)
        num_lines = num_lines - warn_count

    if not has_expected_log_count_symm(num_lines, symmetry_contacts_dict):
        msg = 'Error creating YASARA scene:' \
            ' some commands could not be executed'
        return False, msg

    return success, msg


def has_expected_log_count_ions(found_log_lines, ion_ligand_dict):
    """Returns True if the number of found log lines equals the expected number.

    The expected number of logs is calculated as follows (pseudocode):
        +6 (newline, set CPU number, load PDB, set style, hide all (arrows))
        loop over all ions:
            +2 for ion show, style
            loop over all residues:
                +2 show, style
        +3 (color background, stick, ballstick)
        +10 (list alternate A, center, zoom, save, exit)
    """
    head = 6
    tail = 13
    rest = 0
    for l in ion_ligand_dict.itervalues():
        rest = rest + 2
        for ligres in l[1]:
            rest = rest + 2
    expected = head + rest + tail

    if not found_log_lines == expected:
        _log.error('Number of log lines ({}) not equal to expected number of '
                   'log lines ({})'.format(found_log_lines, expected))
    else:
        _log.debug('Number of log lines ({}) equal to expected number of '
                   'log lines ({})'.format(found_log_lines, expected))

    return found_log_lines == expected
    return True


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
    Also return the number of lines in the file up to the end.
    """
    exit_present = False
    num_lines = 0
    try:
        with open(yasara_log + '.log', 'r') as f:
            for last_line in f:
                num_lines = num_lines + 1
            _log.debug('Log {}.log has {} lines'.format(yasara_log, num_lines))
            if re.search('^>Exit$', last_line):
                _log.debug('Exit found in last line of {}'.format(yasara_log))
                exit_present = True
    except IOError as e:
        _log.error(e)

    return exit_present, num_lines


RE_WARN = re.compile('(WARNING.*?)\n>', re.DOTALL)


def has_logged_warning(yasara_log, warning=None):
    """Checks if 'WARNING' is present in the log.

    Return:
        True when a Warning is found, False otherwise
        The warning itself as a string that may span multiple lines, else None
        The number of lines the warning spans in the YASARA log, else None
    """
    warning_present = False
    warning = None
    warning_lines = None
    try:
        with open(yasara_log + '.log', 'r') as f:
            log = f.read()
            m = re.search(RE_WARN, log)
            if m:
                warning_present = True
                warning = m.group(1)
                warning_lines = warning.count('\n') + 1
                _log.debug('WARNING found in {}: {}'.format(yasara_log,
                                                            warning))
    except IOError as e:
        _log.error(e)
    return warning_present, warning, warning_lines
