import json
import os

from nose.tools import eq_, raises

from yas_scenes.parser import (check_ss2_line_regex, int_check_ss2,
                               parse_ss2_line, parse_sym_contacts)


@raises(TypeError)
def test_check_ss2_line_regex_none():
    """Test that line cannot be None."""
    check_ss2_line_regex(None, None, None, None, None, None, None)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_0():
    """Test proper positioning of ss2 vars."""
    line = '   35SER (  40A)A              0       '
    check_ss2_line_regex(line, None, None, None, None, None, None)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_1():
    """Test proper positioning of ss2 vars."""
    line = '   35 SER (  40A) A              0       '
    check_ss2_line_regex(line, None, None, None, None, None, None)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_2():
    """Test that insertion code is not integer."""
    line = '   35 SER (  401)A              0       '
    check_ss2_line_regex(line, None, None, None, None, None, None)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_3():
    """Test that brace is not bracket."""
    line = '   35 SER [  40A)A              0       '
    check_ss2_line_regex(line, None, None, None, None, None, None)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_4():
    """Test that sequential WHAT IF numbering does not have insertion code."""
    line = '  35A SER (  40A)A              0       '
    check_ss2_line_regex(line, None, None, None, None, None, None)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_5():
    """Test that residue type cannot contain + (example of other characters than
    digits and word characters)."""
    line = '   35 SE+ (  40A)A              0       '
    check_ss2_line_regex(line, None, None, None, None, None, None)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_6():
    """Test that residue number cannot contain character."""
    line = '   35 SER (  4AA)A              0       '
    check_ss2_line_regex(line, None, None, None, None, None, None)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_7():
    """Test that chain cannot be non-word."""
    line = '   35 SER (  40A)@              0       '
    check_ss2_line_regex(line, None, None, None, None, None, None)


@raises(ValueError)
def test_check_ss2_line_regex_nomatch_8():
    """Test that number of contacts cannot be character."""
    line = '   35 SER (  40A)A              A       '
    check_ss2_line_regex(line, None, None, None, None, None, None)


def test_check_ss2_line_regex_ok():
    """Tests that a valid line does not raise any exceptions."""
    line = '   35 SER (  40A)A              0       '
    seq_num = '   35'
    res_typ = 'SER'
    res_num = '  40'
    res_ic = 'A'
    chain = 'A'
    n_contacts = '              0'
    check_ss2_line_regex(line, seq_num, res_typ, res_num, res_ic, chain,
                         n_contacts)

    line = '  160  CL ( 173 )A              2       '
    seq_num = '  160'
    res_typ = ' CL'
    res_num = ' 173'
    res_ic = ' '
    chain = 'A'
    n_contacts = '              2'
    result = check_ss2_line_regex(line, seq_num, res_typ, res_num, res_ic,
                                  chain, n_contacts)
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


@raises(TypeError)
def test_parse_ss2_line_none():
    """Test that line cannot be None."""
    parse_ss2_line(None)


def test_parse_ss2_line_ok():
    """Test that selection string and n_contacts are correctly returned."""
    line = '    1 MET (   1 )A              3       '
    selection, n_contacts = parse_ss2_line(line)
    eq_('1  mol A', selection)
    eq_(3, n_contacts)

    line = '   35 SER (  40A)A              0       '
    selection, n_contacts = parse_ss2_line(line)
    eq_('40A mol A', selection)
    eq_(0, n_contacts)

    line = '  160  CL ( 173 )A              2       '
    selection, n_contacts = parse_ss2_line(line)
    eq_('173  mol A', selection)
    eq_(2, n_contacts)


@raises(IOError)
def test_parse_symm_contacts_ioerr_file_not_found():
    parse_sym_contacts('103l.ss2.bz2')


@raises(IOError)
def test_parse_symm_contacts_ioerr_uncompressed():
    parse_sym_contacts(os.path.join('yas_scenes', 'tests', 'files', '103l.ss2'))


@raises(TypeError)
def test_parse_symm_contacts_none():
    parse_sym_contacts(None)


@raises(ValueError)
def test_parse_symm_contacts_valerr():
    parse_sym_contacts(os.path.join('yas_scenes', 'tests', 'files',
                                    '103l_valerr.ss2.bz2'))


def test_parse_symm_contacts_103l():
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
