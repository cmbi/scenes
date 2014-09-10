from __future__ import division

import logging
_log = logging.getLogger(__name__)

import re

import yasara as yas


RE_YASARA_EXIT = re.compile("^Connection to YASARA broken. Either you exited "
                            "YASARA manually or it encountered a fatal error$")


def prepare_yasara(pid, yasara_log=None, n_threads=1):
    """Prepare YASARA for a parallel setting.

    This means: enable text mode, disable the license screen, assign a unique
    YASARA pid (prevents issues with temporary files created by YASARA),
    disabling the console and disabling multi-threadingsetting.

    If yasara_log is not None, don't disable the console; instead log to
    yasara_log. (If the console if off, commands are not recorded).
    """
    _log.debug("Preparing YASARA in text mode...")
    # Text mode
    yas.info.mode = "txt"

    # Disable license screen
    yas.info.licenseshown = 0

    # Assign a unique yasara PID
    _log.debug("Setting YASARA pid to {}...".format(pid))
    yas.pid = pid

    if yasara_log:
        # Log
        yas.RecordLog(yasara_log, append="No")
        _log.debug("Logging YASARA commands to {}.log...".format(yasara_log))
    else:
        # Disable Console
        _log.debug("Disabling YASARA console...")
        yas.Console("off")

    # Use 1 cpu thread
    _log.debug("Assigning {} cpu threads to YASARA...".format(n_threads))
    yas.Processors(cputhreads=n_threads)


def create_ion_scene(pdb_path, sce_path, ion_sites):
    """Create a YASARA scene displaying ion sites.

    pdb_path is the path to the PDB file
    sce_path is the path of the YASARA scene to be created
    ion_sites is a dictionary of the ion sites to display.
        the keys are YASARA ion atom selection strings (one key = one site):
            <AtomName> res <ResNumber> mol <MolName> e.g.
            'Zn res 316 mol B'
        the values are YASARA residue selection strings (one string for all
        coordinating residues):
            <ResNumber> (<ResNumber> ...) mol <MolName> e.g.
            '190 193 225 227 mol B'

        It is import the numbering of the ions and ligands is PDB numbering
        (and not WHAT IF or other numbering).

    Only the ion sites (ion + ligands) wil be shown, all other atoms are
    hidden.
    The scene is zoomed in on the first ion site.

    RuntimeErrors will be raised if the pdb_path is invalid, if the residue
    name is more than 4 digits, etc.

    Unrealistic selections don't always raise a RuntimeError: non-existing 'Zn'
    or non- existing residue numbers, for example.
    """
    # Load PDB structure
    _log.debug("Loading file {} as structure...".format(pdb_path))
    yas.LoadPDB(pdb_path)

    _log.debug("Making YASARA ion scene...")

    # Hide everything at first
    yas.Style(backbone="stick", sidechain="stick")
    yas.HideAll()

    # Then show the ion sites
    for ion, ligands in ion_sites.iteritems():
        # ions..
        yas.ShowAtom(ion)
        yas.BallAtom(ion)

        # ..and ligands
        yas.ShowRes(ligands)
        yas.StickRes(ligands)

    # Nice visualisation
    yas.ColorBG("000040", "30c0ff")
    yas.StickRadius(percent=40)
    yas.BallStickRadius(ball=50, stick=50)

    # Zoom in on first site
    ion1 = ion_sites.iterkeys().next()
    yas.CenterAtom(ion1, coordsys="Global")
    yas.ZoomAtom(ion1, steps=0)

    # Save scene
    _log.debug("Saving YASARA scene to file {}".format(sce_path))
    yas.SaveSce(sce_path)


def create_sym_scene(pdb_path, sce_path, sym_contacts):
    """Create a YASARA scene displaying the symmetry contacts.

    pdb_path is the path to the PDB file
    sce_path is the path of the YASARA scene to be created
    sym_contacts is a dictionary of the symmetry contacts to display.
        the keys are YASARA residue selection strings (one key = one residue):
            <ResNumber> mol <MolName> e.g.
            '3 Mol A'
        the values incidate the number of symmetry contacts

        It is import the numbering of the ions and ligands is PDB numbering
        (and not WHAT IF or other numbering).

    A Calpha trace will be shown for the structure. Sidechains will be shown
    for residues involved in symmetry contacts.
    A color code indicates the number of symmetry contacts. This number will be
    scaled to be between 0 and 1 by dividing by 10. Everything above 10 will
    then have the same color.
        -999 indicates no property could be assigned to a residue: grey
        0.0: yellow
        1.0: blue

    RuntimeErrors will be raised if the pdb_path is invalid, if the residue
    name is more than 4 digits, etc.

    Unrealistic selections don't always raise a RuntimeError: non-existing 'Zn'
    or non- existing residue numbers, for example.
    """
    # Load PDB structure
    _log.debug("Loading file {} as structure...".format(pdb_path))
    yas.LoadPDB(pdb_path)

    _log.debug("Making YASARA symmetry contacts scene...")

    # Set default style
    yas.Style(backbone="trace", sidechain="off")
    yas.ColorAll("grey")

    # Show residues and color according to property values
    for residue, num_contacts in sym_contacts.iteritems():
        if num_contacts > 0:
            yas.ShowAtom("Sidechain res {}".format(residue))
        yas.PropRes(residue, num_contacts/10)
        yas.ColorRes(residue, "Property")

    # Nice visualisation
    yas.ColorBG("000040", "30c0ff")
    yas.StickRadius(percent=40)
    yas.BallStickRadius(ball=50, stick=50)
    yas.NiceOriAll()

    # Save scene
    _log.debug("Saving YASARA scene to file {}".format(sce_path))
    yas.SaveSce(sce_path)


def exit_yasara():
    """Exit yasara without error code.

    Return True if YASARA terminated normally. We assume this is the case when
    the Exit statement is reached and YASARA exits with the expected
    Exit message.

    Any open YASARA log files will be closed.
    """
    normal_exit = False
    try:
        _log.debug("Closing YASARA...")
        yas.Exit(error=None)
    except RuntimeError as e:
        if re.match(RE_YASARA_EXIT, str(e)):
            _log.debug("It seems YASARA terminated normally")
            return True
    return normal_exit
