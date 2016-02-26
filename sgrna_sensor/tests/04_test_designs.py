#!/usr/bin/env python

import pytest
from sgrna_sensor import *

def test_from_name():
    with pytest.raises(ValueError):
        from_name('')
    with pytest.raises(ValueError):
        from_name('nosuchdesign')

    equivalent_constructs = [
            from_name('us(4)'),
            from_name('us(4,0)'),
            from_name('us(4, 0)'),
            from_name('us 4'),
            from_name('us 4 0'),
            from_name('us/4'),
            from_name('us/4/0'),
            from_name('us-4'),
            from_name('us-4-0'),
            from_name('us_4'),
            from_name('us_4_0'),
    ]

    for construct in equivalent_constructs:
        assert construct.seq == equivalent_constructs[0].seq

    assert from_name('cb') == cb()
    assert from_name('cb/wo') == cb('wo')
    assert from_name('theo/cb') == cb()
    assert from_name('tet/cb') == cb(ligand='tet')

def test_wt_sgrna():
    assert from_name('wt') == 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCAACUUGAAAAAGUGGCACCGAGUCGGUGC' 'UUUUUU'

def test_dead_sgrna():
    assert from_name('dead') == 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AACCCUAGUCCGU' 'UAUCAACUUGAAAAAGUGGCACCGAGUCGGUGC' 'UUUUUU'

def test_fold_upper_stem():
    with pytest.raises(ValueError):
        from_name('us(5)')

    assert from_name('us(4)') == from_name('us(4,0)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAAUACCAGCCGAAAGGCCCUUGGCAGUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('us(2)') == from_name('us(2,0)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCAUACCAGCCGAAAGGCCCUUGGCAGGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('us(0)') == from_name('us(0,0)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAAUACCAGCCGAAAGGCCCUUGGCAGAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('us(4,1)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAUAUACCAGCCGAAAGGCCCUUGGCAGUUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('us(4,7)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAUUUCCCUAUACCAGCCGAAAGGCCCUUGGCAGUUUCCCUUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('us(0,1)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAUAUACCAGCCGAAAGGCCCUUGGCAGUAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('us(0,7)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAUUUCCCUAUACCAGCCGAAAGGCCCUUGGCAGUUUCCCUAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('us(0,0,1)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAAUACCAGCCUGGCCCUUGGCAGAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('us(0,0,7)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAAUACCAGCCUUUCCCUGGCCCUUGGCAGAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('us(0,0,0,2)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAAUACCAGCCAUACCAGCCGAAAGGCCCUUGGCAGGGCCCUUGGCAGAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_fold_lower_stem():
    with pytest.raises(ValueError):
        from_name('ls(7)')

    assert from_name('ls(6,0)') == from_name('ls(6)') == 'GGGGCCACTAGGGACAGGATGUUUUAAUACCAGCCGAAAGGCCCUUGGCAGUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('ls(5,0)') == from_name('ls(5)') == 'GGGGCCACTAGGGACAGGATGUUUUAUACCAGCCGAAAGGCCCUUGGCAGAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('ls(0,0)') == from_name('ls(0)') == 'GGGGCCACTAGGGACAGGATAUACCAGCCGAAAGGCCCUUGGCAGAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('ls(6,1)') == 'GGGGCCACTAGGGACAGGATGUUUUAUAUACCAGCCGAAAGGCCCUUGGCAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('ls(6,7)') == 'GGGGCCACTAGGGACAGGATGUUUUAUUUCCCUAUACCAGCCGAAAGGCCCUUGGCAGUUUCCCUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('ls(0,1)') == 'GGGGCCACTAGGGACAGGATUAUACCAGCCGAAAGGCCCUUGGCAGUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('ls(0,7)') == 'GGGGCCACTAGGGACAGGATUUUCCCUAUACCAGCCGAAAGGCCCUUGGCAGUUUCCCUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_fold_nexus():
    assert from_name('nx(0)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGAUACCAGCCGAAAGGCCCUUGGCAGCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nx(1)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGUAUACCAGCCGAAAGGCCCUUGGCAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nx(6)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGUUUUUUAUACCAGCCGAAAGGCCCUUGGCAGUUUUUUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_fold_nexus_2():
    with pytest.raises(ValueError):
        from_name('nxx(5,0)')
    with pytest.raises(ValueError):
        from_name('nxx(0,6)')
    with pytest.raises(ValueError):
        from_name('nxx(0,0,4)')
    with pytest.raises(ValueError):
        from_name('nxx(0,0,5,0)')

    assert from_name('nxx(0,0)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAAUACCAGCCGAAAGGCCCUUGGCAGGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(1,1)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGAUACCAGCCGAAAGGCCCUUGGCAGCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(2,2)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGAUACCAGCCGAAAGGCCCUUGGCAGCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(2,3)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGAUACCAGCCGAAAGGCCCUUGGCAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(4,5,5)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAUACCAGCCUUUCCGGCCCUUGGCAGAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(4,5,6)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAUACCAGCCUUUCCCGGCCCUUGGCAGAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(4,5,7)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAUACCAGCCUUUCCCUGGCCCUUGGCAGAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(4,5,8)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAUACCAGCCUUUCCCUUGGCCCUUGGCAGAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(4,5,0,2)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAUACCAGCCAUACCAGCCGAAAGGCCCUUGGCAGGGCCCUUGGCAGAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(4,5,0,3)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAUACCAGCCAUACCAGCCAUACCAGCCGAAAGGCCCUUGGCAGGGCCCUUGGCAGGGCCCUUGGCAGAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('nxx(4,5,10,2)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAUACCAGCCAUACCAGCCUUUCCCUUUCGGCCCUUGGCAGGGCCCUUGGCAGAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_fold_hairpin():
    with pytest.raises(ValueError):
        from_name('fh(0,0)')
    with pytest.raises(ValueError):
        from_name('fh(3,0)')
    with pytest.raises(ValueError):
        from_name('fh(1,5)')
    with pytest.raises(ValueError):
        from_name('fh(2,7)')

    assert from_name('fh(1,0)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAAUACCAGCCGAAAGGCCCUUGGCAGGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('fh(1,4)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUAUACCAGCCGAAAGGCCCUUGGCAGAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('fh(2,0)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGAUACCAGCCGAAAGGCCCUUGGCAGUUUUUU'
    assert from_name('fh(2,6)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAUACCAGCCGAAAGGCCCUUGGCAGCGGUGCUUUUUU'

def test_replace_hairpins():
    assert from_name('hp(0)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUAUACCAGCCGAAAGGCCCUUGGCAGUUUUUU'
    assert from_name('hp(18)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGAUACCAGCCGAAAGGCCCUUGGCAGUUUUUU'
    assert from_name('hp(33)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCAUACCAGCCGAAAGGCCCUUGGCAGUUUUUU'
    assert from_name('hp(39)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUCCCAUACCAGCCGAAAGGCCCUUGGCAGUUUUUU'
    assert from_name('hp(49)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUCCCUUUCCCUUUCAUACCAGCCGAAAGGCCCUUGGCAGUUUUUU'

def test_induce_dimerization():
    with pytest.raises(ValueError):
        from_name('id(0,0)')
    with pytest.raises(ValueError):
        from_name('id(hello,0)')
    with pytest.raises(ValueError):
        from_name('id(3,5)')
    with pytest.raises(ValueError):
        from_name('id(3,hello)')

    assert id(5,0,target=None) == 'GUUUUAGAAUACCAGCC'

    assert from_name('id(5,0)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAAUACCAGCC'
    assert from_name('id(5,1)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGAUACCAGCC'
    assert from_name('id(5,2)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCAUACCAGCC'
    assert from_name('id(5,3)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAUACCAGCC'
    assert from_name('id(5,4)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAAUACCAGCC'

    assert from_name('id(3,0)') == 'GGGGCCACTAGGGACAGGATGGCCCUUGGCAGAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('id(3,1)') == 'GGGGCCACTAGGGACAGGATGGCCCUUGGCAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('id(3,2)') == 'GGGGCCACTAGGGACAGGATGGCCCUUGGCAGGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('id(3,3)') == 'GGGGCCACTAGGGACAGGATGGCCCUUGGCAGAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('id(3,4)') == 'GGGGCCACTAGGGACAGGATGGCCCUUGGCAGUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_serpentine_bulge():
    with pytest.raises(ValueError):
        from_name('sb(1)')

    assert from_name('sb(2)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAUCGUAUACCAGCCGAAAGGCCCUUGGCAGACGAAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('sb(8)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAUCGUUAAAAUAUACCAGCCGAAAGGCCCUUGGCAGAUUUUAACGAAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_serpentine_lower_stem():
    assert from_name('sl') == 'GGGGCCACTAGGGACAGGATUCGGCUGAAUACCAGCCGAAAGGCCCUUGGCAGAAGUAGCCGAAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_serpentine_lower_stem_around_nexus():
    assert from_name('slx') == 'GGGGCCACTAGGGACAGGATGUUAUCGAAUACCAGCCGAAAGGCCCUUGGCAGAAGUGAUAACAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_serpentine_hairpin():
    with pytest.raises(ValueError):
        from_name('sh(3)')
    with pytest.raises(ValueError):
        from_name('sh(15)')

    assert from_name('sh(4)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAAACGAUACCAGCCGAAAGGCCCUUGGCAGCGUUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('sh(14)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAAACGGACUAGCCUUAUACCAGCCGAAAGGCCCUUGGCAGAAGGCUAGUCCGUUGGCACCGAGUCGGUGCUUUUUU'

def test_circle_bulge():
    assert from_name('cb') == 'GGGGCCACTAGGGACAGGATGUUUUAACUUAUACCAGCCGAAAGGCCCUUGGCAGAAGUAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_circle_bulge_combo():
    assert from_name('cbc/wo/slx/wo').seq == 'GGGGCCACTAGGGACAGGATGUUGUCACUUAUACCAGCCGAAAGGCCCUUGGCAGAGGUAAGUGAUAACAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('cbc/wo/sh/5') == 'GGGGCCACTAGGGACAGGATGUUUUAACUUAUACCAGCCGAAAGGCCCUUGGCAGAGGUAAGUUAAAAUAAGGCUAGUCCGUUAUCAAACGGAUACCAGCCGAAAGGCCCUUGGCAGCCGUUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('cbc/wo/sh/7') == 'GGGGCCACTAGGGACAGGATGUUUUAACUUAUACCAGCCGAAAGGCCCUUGGCAGAGGUAAGUUAAAAUAAGGCUAGUCCGUUAUCAAACGGACAUACCAGCCGAAAGGCCCUUGGCAGGUCCGUUGGCACCGAGUCGGUGCUUUUUU'

def test_circle_lower_stem():
    assert from_name('cl') == 'GGGGCCACTAGGGACAGGATAGCCUUGAAUACCAGCCGAAAGGCCCUUGGCAGAAGUAAGGCUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_circle_hairpin():
    with pytest.raises(ValueError):
        from_name('sh(3)')
    with pytest.raises(ValueError):
        from_name('sh(19)')

    assert from_name('ch(4)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAAUCAAUACCAGCCGAAAGGCCCUUGGCAGUGAUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('ch(18)') == 'GGGGCCACTAGGGACAGGATGUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAAAGGCUAGUCCGUUAUCAAUACCAGCCGAAAGGCCCUUGGCAGUGAUAACGGACUAGCCUUGGCACCGAGUCGGUGCUUUUUU'

def test_random_bulge():
    assert from_name('rb(4,8)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUA' 'NNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNNNNN' 'UAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('rb(5,7)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUA' 'NNNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNNNN' 'UAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'
    assert from_name('rb(6,6)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUA' 'NNNNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNNN' 'UAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGCUUUUUU'

def test_random_nexus():
    assert from_name('rx(6,6)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AA' 'NNNNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNNN' 'GU' 'UAUCAACUUGAAAAAGUGGCACCGAGUCGGUGC' 'UUUUUU'

def test_random_hairpin():
    assert from_name('rh(6,6)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCA' 'NNNNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNNN' 'GGCACCGAGUCGGUGC' 'UUUUUU'
    assert from_name('rh(6,5)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCA' 'NNNNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNN' 'GGCACCGAGUCGGUGC' 'UUUUUU'
    assert from_name('rh(6,4)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCA' 'NNNNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNN' 'GGCACCGAGUCGGUGC' 'UUUUUU'
    assert from_name('rh(5,6)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCA' 'NNNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNNN' 'GGCACCGAGUCGGUGC' 'UUUUUU'
    assert from_name('rh(5,5)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCA' 'NNNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNN' 'GGCACCGAGUCGGUGC' 'UUUUUU'
    assert from_name('rh(5,4)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCA' 'NNNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNN' 'GGCACCGAGUCGGUGC' 'UUUUUU'
    assert from_name('rh(4,6)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCA' 'NNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNNN' 'GGCACCGAGUCGGUGC' 'UUUUUU'
    assert from_name('rh(4,5)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCA' 'NNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNNN' 'GGCACCGAGUCGGUGC' 'UUUUUU'
    assert from_name('rh(4,4)').seq == 'GGGGCCACTAGGGACAGGAT' 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU' 'AAGGCUAGUCCGU' 'UAUCA' 'NNNN' 'AUACCAGCCGAAAGGCCCUUGGCAG' 'NNNN' 'GGCACCGAGUCGGUGC' 'UUUUUU'
