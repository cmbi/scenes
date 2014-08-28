import logging
_log = logging.getLogger(__name__)

import bz2
import re


RE_SYMM = re.compile("""
                     ^
                     (?P<seq_num>\s*\d+)           # Sequential WHAT IF number
                     [ ]                           #
                     (?P<res_type>[\w ]{2}\w[ \w]) # Residue type WHAT IF
                     \((?P<res_num>[\d -]{3}\d)     # Residue number PDB
                     (?P<res_ic>[A-Z ])\)          # Residue insertion code PDB
                     (?P<chain>\w)                 # Chain
                     (?P<num_contacts>\s+\d+)      # Number of contacts
                     \s*$
                     """, re.VERBOSE)


def check_ss2_line_regex(l, seq_num, res_typ, res_num, res_ic, chain,
                         n_contacts):
    """Checks this ss2 line matches the ss2 regex.

    Return ValueError if the line does not match the ss2 regex or if regex
    groups do not match expected values.
    """
    m = re.match(RE_SYMM, l)
    if not m:
        raise ValueError('Unexpected ss2 file format')


def int_check_ss2(seq_num, res_num, num_contacts):
    """Convert string arguments are integer.

    Return integer values.
    Raise ValueError if string cannot be converted to integer.
    """
    try:
        seq_num = int(seq_num)
    except ValueError:
        raise ValueError('Sequential WHAT IF residue number should be integer')

    try:
        res_num = int(res_num)
    except ValueError:
        raise ValueError('PDB number should be integer')

    try:
        num_contacts = int(num_contacts)
    except ValueError:
        raise ValueError('Number of symmetry contacts should be integer')

    return seq_num, res_num, num_contacts


def parse_ss2_line(l):
    """Extract residue identifier and number of symmetry contacts from ss2 line.

    Return YASARA selection string and number of contacts.
    The YASARA selection string is composed as:
        <PDBResNumberWithInsertionCode> mol <MolName> e.g. '3B mol A'

    The ss2 file has a fixed format so we parse the line directly.
    Simple checks check if the variables parsed from the line have the expected
    type. For extra security, we also check against a regex.
    Raise ValueError if strings of integer vars cannot be parsed to integers.
    Raise ValueError if the line does not match the ss2 regex.
    """
    seq_num = l[0:5]         # Sequential WHAT IF numbering
    res_typ = l[6:10]        # Reside letters WI, 4 for [DR]NA, 3 for protein
    res_num = l[11:15]       # Residue number PDB
    res_ic = l[15:16]        # Residue insertion code PDB
    chain = l[17:18]         # Chain PDB
    num_contacts = l[18:33]  # Number of symmetry contacts for this residue

    # Regex checks
    check_ss2_line_regex(l, seq_num, res_typ, res_num, res_ic, chain,
                         num_contacts)

    # Oversimplified format check
    seq_num, res_num, num_contacts = int_check_ss2(seq_num, res_num,
                                                   num_contacts)

    yasara_residue_selection = '{0:d}{1:s} mol {2:s}'.format(res_num, res_ic,
                                                             chain)

    return yasara_residue_selection, num_contacts


def parse_sym_contacts(ss2):
    """Parse symmetry contacts from a ss2.bz2 file.

    Return a dict of YASARA residue selection strings (keys) and number of
    symmetry contacts (values):
        {'<ResNumberWithInsertionCode> mol <MolName>': 1}
    Residue insertion codes are included in the residue number.

    Raise IOError if the file cannot be read properly.
    Raise ValueError if the format of the file is incorrect.
    """
    symm_cont = {}
    try:
        with bz2.BZ2File(ss2, 'r') as f:
            for line in f:
                if not line.startswith('*END'):
                    line = line.rstrip()
                    select, n_contacts = parse_ss2_line(line)
                    symm_cont[select] = n_contacts
    except IOError as e:
        _log.error(e)
        raise(IOError('Problem reading {}'.format(ss2)))
    except ValueError as e:
        _log.error(e)
        raise e

    return symm_cont
