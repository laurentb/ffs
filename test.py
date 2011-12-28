from ffs import Router, Dict, DictList, RouterError
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

    def test_copyTrees(self):
        rtr = Router(lol=Router(cat=str), lulz=Router(cat=str))
        lst1 = Dict(self.root, rtr)
        lst1['lulz'] = lst1['lol']
        assert 'cat' in lst1['lulz']
        assert lst1['lulz']['cat'] == "hello"

    def test_intTypeConv(self):
        lst1 = Dict(self.root, Router(lulz=int))
        assert 'lulz' not in lst1
        lst1['lulz'] = 42
        assert lst1['lulz'] == 42
        assert isinstance(lst1['lulz'], int)
        lst1['lulz'] += 1
        assert lst1['lulz'] == 43
        assert isinstance(lst1['lulz'], int)

        lst2 = Dict(self.root, Router(lulz=str))
        assert lst2['lulz'] == "43"
        assert isinstance(lst2['lulz'], basestring)

    def test_customTypeConv(self):
        class Rot13(object):
            """
            Protect your data from hackers reading your memory!
            """
            def __init__(self, encstring):
                self.encstring = encstring

            def __str__(self):
                return 'ENCRYPTED!'

            def tostring(self):
                return self.encstring.encode('rot13')

            @classmethod
            def fromstring(cls, string):
                return cls(string.decode('rot13'))

        rot13 = Rot13('yby')
        assert rot13.tostring() == 'lol'
        assert Rot13.fromstring('lol').tostring() == 'lol'

        lst1 = Dict(self.root, Router(lulz=Rot13))
        lst1['lulz'] = Rot13('yby')
        assert lst1['lulz'].tostring() == 'lol'
        assert isinstance(lst1['lulz'], Rot13)

        lst2 = Dict(self.root, Router(lulz=str))
        assert lst2['lulz'] == "lol"
        assert isinstance(lst2['lulz'], basestring)

    def test_DictList(self):
        rtr = Router(looool=[str])
        lst1 = Dict(self.root, rtr)
        self.assertRaises(KeyError, lst1.__getitem__, 'looool')
        os.mkdir(os.path.join(self.root, 'looool'))
        assert isinstance(lst1['looool'], DictList)
        dl1 = lst1['looool']
        # validate index types (mimics list)
        self.assertRaises(TypeError, dl1.__getitem__, 'lulz')
        # no elements, can't do anything (mimics list)
        self.assertRaises(IndexError, dl1.__getitem__, 0)
        self.assertRaises(IndexError, dl1.__setitem__, 0, 'a')
        self.assertRaises(IndexError, dl1.__delitem__, 0)
        assert len(dl1) == 0
        # add an element
        dl1.append('b')
        assert len(dl1) == 1
        assert dl1[0] == 'b'
        # alter the element
        dl1[0] = 'c'
        assert dl1[0] == 'c'
        # check it's the same with a new DictList instance
        dl2 = lst1['looool']
        assert dl1 is not dl2
        assert dl2[0] == 'c'
        # check order
        dl1.append('d')
        dl1.append('e')
        assert dl1[0] == 'c'
        assert dl1[1] == 'd'
        assert dl1[2] == 'e'
        assert len(dl1) == 3
        # deletion
        del dl1[1]
        assert dl1[0] == 'c'
        assert dl1[1] == 'e'
        assert len(dl1) == 2
        self.assertRaises(IndexError, dl1.__delitem__, 2)
        del dl1[1]
        assert dl1[0] == 'c'
        assert len(dl1) == 1
        del dl1[0]
        assert len(dl1) == 0
        # insertion
        dl1.insert(0, 'a')
        dl1.insert(0, 'b')
        dl1.insert(0, 'c')
        assert dl1[0] == 'c'
        assert dl1[1] == 'b'
        assert dl1[2] == 'a'
        assert len(dl1) == 3
        del dl1[2]
        dl1.insert(1, 'd')
        assert dl1[0] == 'c'
        assert dl1[1] == 'd'
        assert dl1[2] == 'b'
        assert len(dl1) == 3
        dl1.insert(42, 'e')
        assert dl1[3] == 'e'
        assert len(dl1) == 4
        dl1.insert(3, 'f')
        assert dl1[3] == 'f'
        assert dl1[4] == 'e'
        assert len(dl1) == 5
        # negative indexes
        assert dl1[-1] == dl1[4]
        assert dl1[-2] == dl1[3]
        assert dl1[-3] == dl1[2]
        assert dl1[-4] == dl1[1]
        assert dl1[-5] == dl1[0]
        self.assertRaises(IndexError, dl1.__getitem__, -6)
        # erase/copy whole list
        del lst1['looool']
        assert 'looool' not in lst1
        lst1['looool'] = ['x', 'y']
        assert len(lst1['looool']) == 2
        assert len(dl1) == 2
        assert dl1[0] == 'x'
        assert dl1[1] == 'y'
        lst1['looool'] = []
        assert 'looool' in lst1
        assert len(dl1) == 0
