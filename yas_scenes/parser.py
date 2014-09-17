import logging
_log = logging.getLogger(__name__)

import bz2
import re


RE_SYMM = re.compile("""
                     ^
                     (?P<seq_num>\s*\d+)           # Sequential WHAT IF number
                     [ ]                           #
                     (?P<res_type>\s*\w[ \w]{0,3}) # Residue type WHAT IF
                     \((?P<res_num>[\d -]{3}\d)    # Residue number PDB
                     (?P<res_ic>[A-Z ])\)          # Residue insertion code PDB
                     (?P<chain>\w)                 # Chain
                     (?P<num_contacts>\s+\d+)      # Number of contacts
                     \s*$
                     """, re.VERBOSE)


RE_ION = re.compile("""
                    ^
                    (?P<seq_num>\s*\d+)           # Sequential WHAT IF number
                    [ ]                           #
                    (?P<res_type>\s*\w[ \w]{0,3}) # Residue type WHAT IF
                    \((?P<res_num>[\d -]{3}\d)    # Residue number PDB
                    (?P<res_ic>[A-Z ])\)          # Residue insertion code PDB
                    (?P<chain>\w)                 # Chain
                    \s+
                    (?P<atom>[A-Z][A-Z \d']{2,3}) # Atom name
                    \s-\s+
                    (?P<ion_num>\s*\d+)           # Sequential WHAT IF number
                    [ ]                           #
                    (?P<ion_type>\s*\w[ \w]{0,3}) # Residue type WHAT IF
                    \((?P<ion_pnum>[\d -]{3}\d)   # Residue number PDB
                    (?P<ion_ic>[A-Z ])\)          # Residue insertion code PDB
                    (?P<ion_chain>\w)             # Chain WHAT IF
                    \s+
                    (?P<ion_chain_pdb>[\w ])      # Chain PDB
                    \s+
                    (?P<ion>[A-Z][A-Z\d ]+)       # Ion atom name
                    \s+
                    (?P<dist>\d\.\d{3})           # Atom-ion distance
                    \s*$
                    """, re.VERBOSE)


def check_ss2_line_regex(l):
    """Checks this ss2 line matches the ss2 regex.

    Raise ValueError if the line does not match the ss2 regex.
    """
    m = re.match(RE_SYMM, l)
    if not m:
        raise ValueError("Unexpected ss2 file format: '{}'".format(l))


def check_iod_line_regex(l):
    """Checks this iod line matches the iod regex.

    Raise ValueError if the line does not match the iod regex.
    """
    m = re.match(RE_ION, l)
    if not m:
        raise ValueError("Unexpected iod file format: '{}'".format(l))


def int_check_ss2(seq_num, res_num, num_contacts):
    """Convert string arguments to integers.

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
        raise ValueError('Number of crystal contacts should be integer')

    return seq_num, res_num, num_contacts


def int_check_iod(seq_num, res_num, ion_num, ion_pnum, dist):
    """Convert string arguments to integers and float.

    Return integer values or float value.
    Raise ValueError if string cannot be converted to integer or float.
    """
    try:
        seq_num = int(seq_num)
        ion_num = int(ion_num)
    except ValueError:
        raise ValueError('Sequential WHAT IF residue number should be integer')

    try:
        res_num = int(res_num)
        ion_pnum = int(ion_pnum)
    except ValueError:
        raise ValueError('PDB number should be integer')

    try:
        dist = float(dist)
    except ValueError:
        raise ValueError('Ion-ligand distance should be a float')

    return seq_num, res_num, ion_num, ion_pnum, dist


def parse_ss2_line(l):
    """Extract residue identifier and number of crystal contacts from ss2 line.

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
    # res_typ = l[6:10]      # Reside letters WI, 4 for [DR]NA, 3 for protein
    res_num = l[11:15]       # Residue number PDB
    res_ic = l[15:16]        # Residue insertion code PDB
    res_ic = res_ic.strip()
    chain = l[17:18]         # Chain PDB
    num_contacts = l[18:33]  # Number of symmetry contacts for this residue

    # Regex checks
    check_ss2_line_regex(l)

    # Oversimplified format check
    seq_num, res_num, num_contacts = int_check_ss2(seq_num, res_num,
                                                   num_contacts)

    yasara_residue_selection = '{0:d}{1:s} mol {2:s}'.format(res_num, res_ic,
                                                             chain)

    return yasara_residue_selection, num_contacts


def parse_iod_line(l):
    """Extract ion, residue, and atom selections plus distance from iod line.

    Return YASARA selection strings for ion, residue, and atom;
        plus the PDB name of the ion and distance between ion and ligand atom.
    The YASARA selection string for the ion is composed as:
        res <PDBResNumberWithInsertionCode> mol <MolName>
        e.g. 'res 262  mol A'

    The YASARA selection string for the residue is composed as:
        <PDBResNumberWithInsertionCode> mol <MolName>
        e.g. '96  mol A'

    The YASARA selection string for the atom is composed as:
        <PDBAtomName res PDBResNumberWithInsertionCode> mol <MolName>'
        e.g. 'ND1 res 96  mol A'

    The iod file has a fixed format so we parse the line directly.
    Simple checks check if the variables parsed from the line have the expected
    type. For extra security, we also check against a regex.

    Raise ValueError if strings of integer vars cannot be parsed to integers.
    Raise ValueError if the line does not match the iod regex.
    """
    seq_num = l[0:5]         # Sequential WHAT IF numbering
    res_num = l[11:15]       # Residue number PDB
    res_ic = l[15:16]        # Residue insertion code PDB
    chain = l[17:18]         # Chain PDB
    atom = l[24:28]          # Atom name
    atom = atom.strip()
    ion_num = l[31:36]       # Sequential WHAT IF numbering
    ion_pnum = l[42:46]      # Residue number PDB
    ion_ic = l[46:47]        # Residue insertion code PDB
    ion_chain = l[48:49]     # Chain WHAT IF
    ion_pchain = l[52:53]    # Chain PDB
    ion = l[55:57]           # Ion atom name
    ion = ion.strip()
    dist = l[64:69]          # Ligand atom-ion distance

    # Process a bit
    res_ic = res_ic.strip()
    ion_ic = ion_ic.strip()
    ion_chain = ion_pchain if ion_pchain != ' ' else ion_chain

    # Regex checks
    check_iod_line_regex(l)

    # Oversimplified format check
    seq_num, res_num, ion_num, ion_pnum, dist = int_check_iod(seq_num, res_num,
                                                              ion_num,
                                                              ion_pnum,
                                                              dist)

    yasara_ion_selection = 'res {0:d}{1:s} mol {2:s}'.format(ion_pnum, ion_ic,
                                                             ion_chain)
    yasara_residue_selection = '{0:d}{1:s} mol {2:s}'.format(res_num, res_ic,
                                                             chain)
    yasara_atom_selection = '{0:s} res {1:d}{2:s} mol {3:s}'.format(atom,
                                                                    res_num,
                                                                    res_ic,
                                                                    chain)
    return yasara_ion_selection, ion, yasara_residue_selection, \
        yasara_atom_selection, dist


def parse_sym_contacts(ss2):
    """Parse crystal contacts from a ss2.bz2 file.

    Return a dict of YASARA residue selection strings (keys) and number of
    crystal contacts (values):
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


def parse_ion_sites(iod):
    """Parse metal ion sites from an iod.bz2 file.

    Return a dict:

        The keys are YASARA residue selection strings for the ion (its in its
        own residue):
            res <PDBResNumberWithInsertionCode> mol <MolName>
            e.g. 'res 262 mol A'
        The values are lists:
            The first element is the PDB atom name e.g. 'ZN'

            The second element is a list of YASARA selection strings
            of residues bound to the ion.
            <PDBResNumberWithInsertionCode> mol <MolName>
            e.g. ['94  mol A', '96  mol A', '106  mol A', '119  mol A']

            The third element is a dict
            The keys are YASARA atom selection strings (as above)
            The values are distances defined by the atom to the ion.

        {'res <ResNumberWithInsertionCode> mol <MolName>':
            ['<PDBAtomName>',
             [<PDBResNumberWithInsertionCode> mol <MolName>, ],
             {<PDBAtomName> res <ResNumberWithInsertionCode> mol <MolName>:
             distance}]},

    Residue insertion codes are included in the residue number.

    Raise IOError if the file cannot be read properly.
    Raise ValueError if the format of the file is incorrect.
    """
    ion_sites = {}
    try:
        with bz2.BZ2File(iod, 'r') as f:
            for line in f:
                if not line.startswith('*END'):
                    line = line.rstrip()
                    ion, ion_name, residue, atom, dist = parse_iod_line(line)
                    if ion not in ion_sites:
                        ion_sites[ion] = [ion_name, [residue], {atom: dist}]
                    else:
                        ion_sites[ion][1].append(residue)
                        ion_sites[ion][2][atom] = dist

    except IOError as e:
        _log.error(e)
        raise(IOError('Problem reading {}'.format(iod)))
    except ValueError as e:
        _log.error(e)
        raise e

    return ion_sites
