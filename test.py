from ffs import Router, Dict, RouterError
from tempfile import mkdtemp
import os
import shutil
from unittest import TestCase


class FfsTest(TestCase):
    def setUp(self):
        self.root = mkdtemp(prefix='ffs_test_root')
        os.makedirs(os.path.join(self.root, 'lol'))
        with open(os.path.join(self.root, 'lol', 'cat'), 'w') as f:
            f.write("hello")

    def tearDown(self):
        if self.root:
            shutil.rmtree(self.root)

    def test_simpleAccess1(self):
        rtr = Router(lol=Router(hop=str))
        lst1 = Dict(self.root, rtr)
        assert 'hop' not in lst1
        assert 'lol' in lst1
        lst2 = lst1['lol']
        assert 'hop' not in lst2

    def test_simpleAccess2(self):
        rtr = Router(lol=Router(cat=str))
        lst1 = Dict(self.root, rtr)
        assert 'cat' not in lst1
        assert 'lol' in lst1
        lst2 = lst1['lol']
        assert 'cat' in lst2
        assert "hello" == lst2['cat']

    def test_globAccess1(self):
        with open(os.path.join(self.root, 'lol', 'caaaaat'), 'w') as f:
            f.write("hello2")
        with open(os.path.join(self.root, 'lol', 'longcat'), 'w') as f:
            f.write("hello3")

        rtr = Router(lol=Router({'c*t': str}))
        lst1 = Dict(self.root, rtr)
        assert 'cat' not in lst1
        assert 'lol' in lst1
        lst2 = lst1['lol']
        assert 'cat' in lst2
        assert 'caaaaat' in lst2
        assert 'cot' not in lst2
        assert 'longcat' not in lst2
        assert "hello" == lst2['cat']
        assert "hello2" == lst2['caaaaat']
        self.assertRaises(KeyError, lst2.__getitem__, 'cot')
        self.assertRaises(RouterError, lst2.__getitem__, 'longcat')

    def test_finalValueDelete(self):
        rtr = Router(lol=Router(cat=str))
        lst1 = Dict(self.root, rtr)
        lst2 = lst1['lol']
        assert 'cat' in lst2
        del lst2['cat']
        assert 'cat' not in lst2

    def test_finalValueSet(self):
        rtr = Router(lol=Router(cat=str, cot=str))
        lst1 = Dict(self.root, rtr)
        lst2 = lst1['lol']
        assert 'cot' not in lst2
        lst2['cot'] = "hello2"
        assert 'cot' in lst2
        assert lst2['cot'] == "hello2"

    def test_listDelete(self):
        rtr = Router(lol=Router(cat=str, cot=str))
        lst1 = Dict(self.root, rtr)
        assert 'lol' in lst1
        del lst1['lol']
        assert 'lol' not in lst1

    def test_listSet(self):
        rtr = Router(lulz=Router(cat=str))
        lst1 = Dict(self.root, rtr)
        assert 'lulz' not in lst1
        lst1['lulz'] = {}
        assert len(lst1['lulz']) == 0
        assert isinstance(lst1['lulz'], Dict)
        lst1['lulz'] = {'cat': "hello"}
        assert len(lst1['lulz']) == 1
        assert isinstance(lst1['lulz'], Dict)

        lst1n = Dict(self.root, rtr)
        assert lst1n['lulz']['cat'] == "hello"

        lst1n['lulz'] = {}
        assert 'cat' not in lst1['lulz']
        assert 'cat' not in lst1n['lulz']
