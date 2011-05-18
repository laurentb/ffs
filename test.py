from ffs import Router, List
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

    def test1(self):
        rtr = Router()
        lst1 = List(self.root, rtr)
        rtr.register('lol', List).register('hop', str)
        assert 'hop' not in lst1
        assert 'lol' in lst1
        lst2 = lst1['lol']
        assert 'hop' not in lst2

    def test2(self):
        rtr = Router()
        lst1 = List(self.root, rtr)
        rtr.register('lol', List).register('cat', str)
        assert 'cat' not in lst1
        assert 'lol' in lst1
        lst2 = lst1['lol']
        assert 'cat' in lst2
        assert "hello" == lst2['cat']
