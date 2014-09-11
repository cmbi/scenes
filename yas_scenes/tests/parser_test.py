import json
import os

from nose.tools import eq_, ok_, raises

from yas_scenes.parser import (check_iod_line_regex, int_check_iod,
                               check_ss2_line_regex, int_check_ss2,
                               parse_iod_line, parse_ion_sites,
                               parse_ss2_line, parse_sym_contacts)


@raises(TypeError)
def test_check_iod_line_regex_none():
    """Test that line cannot be None."""
    check_iod_line_regex()


@raises(ValueError)
def test_check_iod_line_regex_nomatch_0():
    """Test proper positioning of ss2 vars."""
    line = '   93 HIS (  94 )A         N -   262  ZN ( 262 )A      ' +\
           'ZN       2.191'
    check_iod_line_regex(line)


@raises(ValueError)
def test_check_iod_line_regex_nomatch_1():
    """Test proper positioning of ss2 vars."""
    line = '   93 HIS (  94 )A       NE2-   262  ZN ( 262 )A      ' +\
           'ZN       2.191'
    check_iod_line_regex(line)


@raises(ValueError)
def test_check_iod_line_regex_nomatch_2():
    """Test proper positioning of ss2 vars."""
    line = '   93 HIS (  94 )A       NE2 -   262  ZN ( 262 )A      ' +\
           '1ION     2.191'
    check_iod_line_regex(line)


@raises(ValueError)
def test_check_iod_line_regex_nomatch_3():
    """Test proper positioning of ss2 vars."""
    line = '   93 HIS (  94 )A       NE2 -   262  ZN ( 262 )A      ' +\
           'ZN       2.19'
    check_iod_line_regex(line)


def test_check_iod_line_regex_ok():
    """Tests that a valid line does not raise any exceptions."""
    # Zn
    line = '   93 HIS (  94 )A       NE2 -   262  ZN ( 262 )A      ' +\
           'ZN       2.191'
    result = check_iod_line_regex(line)
    eq_(result, None)

    # Hg
    line = '  136 PRO ( 138 )A       N   -   263  HG ( 495 )A      ' +\
           'HG       4.063'
    result = check_iod_line_regex(line)
    eq_(result, None)

    # Na
    line = "  251 SAM ( 501 )A       O3' -   259  NA ( 820 )A      " +\
           "NA       4.221"
    result = check_iod_line_regex(line)
    eq_(result, None)

    # K
    line = '  307 ASN ( 309 )A       O   -   832 K   (1419 )A      ' +\
           ' K       2.757'
    result = check_iod_line_regex(line)
    eq_(result, None)

    # CA
    line = '    6 CGU (   6 )L      OE11 -   594  CA ( 505 )L      ' +\
           'CA       2.941'
    result = check_iod_line_regex(line)
    eq_(result, None)

    # Mg
    line = '  330 MSE ( 352 )A      SE   -  1844  MG ( 501 )A      ' +\
           'MG       4.268'
    result = check_iod_line_regex(line)
    eq_(result, None)

    # Mn+ 1svv
    line = '   23 ASP (  37 )A       OD1 -   683 UNL ( 401 )A      ' +\
           'MN1      2.430'
    result = check_iod_line_regex(line)
    eq_(result, None)

    # Pt+ 4g49
    line = '   14 ARG (  14 )A       NH2 -   135 CPT ( 206 )A      ' +\
           'PT1      2.727'
    result = check_iod_line_regex(line)
    eq_(result, None)

    # Rh+ 4gjv
    line = '  115 HIS ( 127 )A       NE2 -   126  RH ( 403 )A      ' +\
           'RH1      2.269'
    result = check_iod_line_regex(line)
    eq_(result, None)

    # UNL 3tv2
    line = '  135 SER ( 279 )A       OG  -   459 UNL ( 604 )A      ' +\
           ' UNL     3.410'
    result = check_iod_line_regex(line)
    eq_(result, None)


@raises(ValueError)
def test_int_check_iod_seq_num():
    """Test that seq_num cannot be character."""
    int_check_iod(seq_num='A', res_num='1', ion_num='1', ion_pnum='1',
                  dist=1.000)


@raises(ValueError)
def test_int_check_iod_res_num():
    """Test that res_num cannot be character."""
    int_check_iod(seq_num='1', res_num='A', ion_num='1', ion_pnum='1',
                  dist=1.000)


@raises(ValueError)
def test_int_check_iod_ion_num():
    """Test that ion_num cannot be character."""
    int_check_iod(seq_num='1', res_num='1', ion_num='A', ion_pnum='1',
                  dist=1.000)


@raises(ValueError)
def test_int_check_iod_ion_pnum():
    """Test that ion_pnum cannot be character."""
    int_check_iod(seq_num='1', res_num='1', ion_num='1', ion_pnum='A',
                  dist=1.000)


@raises(ValueError)
def test_int_check_iod_dist():
    """Test that dist cannot be character."""
    int_check_iod(seq_num='1', res_num='1', ion_num='1', ion_pnum='1',
                  dist='A')


def test_int_check_iod_ok():
    """Test that arguments can be parsed to int and float."""
    int_check_iod(seq_num='1', res_num='1', ion_num='1', ion_pnum='1',
                  dist=1.000)


@raises(TypeError)
def test_parse_iod_line_none():
    """Test that line cannot be None."""
    parse_iod_line(None)


def test_parse_iod_line_ok():
    """Test that ion, residue selection string, atom selection string,
       and distance are correctly returned."""

    line = '   93 HIS (  94 )A       NE2 -   262  ZN ( 262 )A      ' +\
           'ZN       2.191'
    ion, ion_name, residue, atom, dist = parse_iod_line(line)
    eq_('res 262 mol A', ion)
    eq_('ZN', ion_name)
    eq_('94 mol A', residue)
    eq_('NE2 res 94 mol A', atom)
    eq_(2.191, dist)

    line = '  136 PRO ( 138 )A       N   -   263  HG ( 495 )A      ' +\
           'HG       4.063'
    ion, ion_name, residue, atom, dist = parse_iod_line(line)
    eq_('res 495 mol A', ion)
    eq_('HG', ion_name)
    eq_('138 mol A', residue)
    eq_('N res 138 mol A', atom)
    eq_(4.063, dist)

    line = "  251 SAM ( 501 )A       O3' -   259  NA ( 820 )A      " +\
           "NA       4.221"
    ion, ion_name, residue, atom, dist = parse_iod_line(line)
    eq_('res 820 mol A', ion)
    eq_('NA', ion_name)
    eq_('501 mol A', residue)
    eq_("O3' res 501 mol A", atom)
    eq_(4.221, dist)

    line = '  307 ASN ( 309 )A       O   -   832 K   (1419 )A       ' +\
           'K       2.757'
    ion, ion_name, residue, atom, dist = parse_iod_line(line)
    eq_('res 1419 mol A', ion)
    eq_('K', ion_name)
    eq_('309 mol A', residue)
    eq_('O res 309 mol A', atom)
    eq_(2.757, dist)

    line = '    6 CGU (   6 )L      OE11 -   594  CA ( 505 )L      ' +\
           'CA       2.941'
    ion, ion_name, residue, atom, dist = parse_iod_line(line)
    eq_('res 505 mol L', ion)
    eq_('CA', ion_name)
    eq_('6 mol L', residue)
    eq_('OE11 res 6 mol L', atom)
    eq_(2.941, dist)

    line = '  330 MSE ( 352 )A      SE   -  1844  MG ( 501 )A      ' +\
           'MG       4.268'
    ion, ion_name, residue, atom, dist = parse_iod_line(line)
    eq_('res 501 mol A', ion)
    eq_('MG', ion_name)
    eq_('352 mol A', residue)
    eq_('SE res 352 mol A', atom)
    eq_(4.268, dist)


@raises(IOError)
def test_parse_ion_sites_ioerr_file_not_found():
    """Test that IOError is raised if file path is incorrect."""
    parse_ion_sites('1cra.iod.bz2')


@raises(IOError)
def test_parse_ion_sites_contacts_ioerr_uncompressed():
    """Test that an IOError is raised if iod file is uncompressed."""
    parse_ion_sites(os.path.join(
        'yas_scenes', 'tests', 'files', '1cra.iod'))


@raises(TypeError)
def test_parse_ion_sites_none():
    """Test that TypeError is raised if iod file path is None."""
    parse_ion_sites(None)


@raises(ValueError)
def test_parse_ion_sites_valerr():
    """Test that ValueError is raised if iod file has incorrect content."""
    parse_ion_sites(os.path.join('yas_scenes', 'tests', 'files',
                                 '1cra_valerr.iod.bz2'))


def test_parse_symm_contacts_1cra():
    """Test that 1cra.iod.bz2 is parsed correctly.

    1cra contains protein, ZN and HG
    """
    try:
        with open(os.path.join('yas_scenes', 'tests', 'files',
                               '1cra.iod.json'), 'r') as f:
            ion_sites = json.load(f)
    except IOError as e:
        raise e

    result = parse_ion_sites(os.path.join('yas_scenes', 'tests', 'files',
                                          '1cra.iod.bz2'))
    eq_(len(ion_sites), len(result))
    for k, v in ion_sites.iteritems():
        ion = v
        result_ion = result[k]
        eq_(len(ion), len(result_ion))
        eq_(ion[0], result_ion[0])
        eq_(len(ion[1]), len(result_ion[1]))
        eq_(len(ion[2]), len(result_ion[2]))
        for res in ion[1]:
            assert res in result_ion[1]
        for l, w in ion[2].iteritems():
            eq_(w, result_ion[2][l])


@raises(TypeError)
def test_check_ss2_line_regex_none():
    """Test that line cannot be None."""
    check_ss2_line_regex()


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_0():
    """Test proper positioning of ss2 vars."""
    line = '   35SER (  40A)A              0       '
    check_ss2_line_regex(line)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_1():
    """Test proper positioning of ss2 vars."""
    line = '   35 SER (  40A) A              0       '
    check_ss2_line_regex(line)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_2():
    """Test that insertion code is not integer."""
    line = '   35 SER (  401)A              0       '
    check_ss2_line_regex(line)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_3():
    """Test that brace is not bracket."""
    line = '   35 SER [  40A)A              0       '
    check_ss2_line_regex(line)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_4():
    """Test that sequential WHAT IF numbering does not have insertion code."""
    line = '  35A SER (  40A)A              0       '
    check_ss2_line_regex(line)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_5():
    """Test that residue type cannot contain + (example of other characters
    than digits and word characters)."""
    line = '   35 SE+ (  40A)A              0       '
    check_ss2_line_regex(line)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_6():
    """Test that residue number cannot contain character except dash."""
    line = '   35 SER (  4AA)A              0       '
    check_ss2_line_regex(line)

    line = '    1 GLY (  -1 )A              0       '
    check_ss2_line_regex(line)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_7():
    """Test that chain cannot be non-word."""
    line = '   35 SER (  40A)@              0       '
    check_ss2_line_regex(line)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_8():
    """Test that number of contacts cannot be character."""
    line = '   35 SER (  40A)A              A       '
    check_ss2_line_regex(line)


def test_check_ss2_line_regex_ok():
    """Tests that a valid line does not raise any exceptions."""
    # Amino acid
    line = '   35 SER (  40A)A              0       '
    result = check_ss2_line_regex(line)
    eq_(result, None)

    # Halide
    line = '  160  CL ( 173 )A              2       '
    result = check_ss2_line_regex(line)
    eq_(result, None)

    # Metal
    line = ' 2137 NA  ( 401 )A              0       '
    result = check_ss2_line_regex(line)
    eq_(result, None)

    # DNA
    line = '    1 DTHY(4001 )A              4       '
    result = check_ss2_line_regex(line)
    eq_(result, None)

    # RNA
    line = '  152 OADE(   5 )B             10       '
    result = check_ss2_line_regex(line)
    eq_(result, None)

    # Negative PDB number start
    line = '    1 GLY (  -1 )A              0       '
    result = check_ss2_line_regex(line)
    eq_(result, None)


@raises(ValueError)
def test_int_check_ss2_seq_num():
    """Test that seq_num cannot be character."""
    int_check_ss2(seq_num='A', res_num='1', num_contacts='0')


@raises(ValueError)
def test_int_check_ss2_res_num():
    """Test that res_num cannot be character."""
    int_check_ss2(seq_num='1', res_num='A', num_contacts='0')


@raises(ValueError)
def test_int_check_ss2_n_contacts():
    """Test that n_contacts cannot be character."""
    int_check_ss2(seq_num='1', res_num='1', num_contacts='A')


def test_int_check_ss2_res_num_ok():
    """Test that res_num int string can be parsed to int."""
    ok_(int_check_ss2(seq_num='1', res_num='-1', num_contacts='0'))


@raises(TypeError)
def test_parse_ss2_line_none():
    """Test that line cannot be None."""
    parse_ss2_line(None)


def test_parse_ss2_line_ok():
    """Test that selection string and n_contacts are correctly returned."""
    line = '    1 MET (   1 )A              3       '
    selection, n_contacts = parse_ss2_line(line)
    eq_('1 mol A', selection)
    eq_(3, n_contacts)

    line = '   35 SER (  40A)A              0       '
    selection, n_contacts = parse_ss2_line(line)
    eq_('40A mol A', selection)
    eq_(0, n_contacts)

    line = '  160  CL ( 173 )A              2       '
    selection, n_contacts = parse_ss2_line(line)
    eq_('173 mol A', selection)
    eq_(2, n_contacts)

    line = '    1 DTHY(4001 )A              4       '
    selection, n_contacts = parse_ss2_line(line)
    eq_('4001 mol A', selection)
    eq_(4, n_contacts)

    line = '  152 OADE(   5 )B             10       '
    selection, n_contacts = parse_ss2_line(line)
    eq_('5 mol B', selection)
    eq_(10, n_contacts)

    line = '    1 GLY (  -1 )A              0       '
    selection, n_contacts = parse_ss2_line(line)
    eq_('-1 mol A', selection)
    eq_(0, n_contacts)


@raises(IOError)
def test_parse_symm_contacts_ioerr_file_not_found():
    """Test that IOError is raised if file path is incorrect."""
    parse_sym_contacts('103l.ss2.bz2')


@raises(IOError)
def test_parse_symm_contacts_ioerr_uncompressed():
    """Test that an IOError is raised if ss2 file is uncompressed."""
    parse_sym_contacts(os.path.join(
        'yas_scenes', 'tests', 'files', '103l.ss2'))


@raises(TypeError)
def test_parse_symm_contacts_none():
    """Test that TypeError is raised if ss2 file path is None."""
    parse_sym_contacts(None)


@raises(ValueError)
def test_parse_symm_contacts_valerr():
    """Test that ValueError is raised if ss2 file has incorrect content."""
    parse_sym_contacts(os.path.join('yas_scenes', 'tests', 'files',
                                    '103l_valerr.ss2.bz2'))


def test_parse_symm_contacts_103l():
    """Test that 103l.ss2.bz2 is parsed correctly.

    103l contains protein and halides
    """
    try:
        with open(os.path.join('yas_scenes', 'tests', 'files',
                               '103l.ss2.json'), 'r') as f:
            symm_contacts = json.load(f)
    except IOError as e:
        raise e

    result = parse_sym_contacts(os.path.join('yas_scenes', 'tests', 'files',
                                             '103l.ss2.bz2'))
    eq_(len(symm_contacts), len(result))
    for k, v in symm_contacts.iteritems():
        eq_(result[k], v)


def test_parse_symm_contacts_1a02():
    """Test that 1a02.ss2.bz2 is parsed correctly.

    1a02 contains DNA and protein
    """
    try:
        with open(os.path.join('yas_scenes', 'tests', 'files',
                               '1a02.ss2.json'), 'r') as f:
            symm_contacts = json.load(f)
    except IOError as e:
        raise e

    result = parse_sym_contacts(os.path.join('yas_scenes', 'tests', 'files',
                                             '1a02.ss2.bz2'))
    eq_(len(symm_contacts), len(result))
    for k, v in symm_contacts.iteritems():
        eq_(result[k], v)


def test_parse_symm_contacts_1a34():
    """Test that 1a34.ss2.bz2 is parsed correctly.

    1a34 contains RNA and protein
    """
    try:
        with open(os.path.join('yas_scenes', 'tests', 'files',
                               '1a34.ss2.json'), 'r') as f:
            symm_contacts = json.load(f)
    except IOError as e:
        raise e

    result = parse_sym_contacts(os.path.join('yas_scenes', 'tests', 'files',
                                             '1a34.ss2.bz2'))
    eq_(len(symm_contacts), len(result))
    for k, v in symm_contacts.iteritems():
        eq_(result[k], v)
