#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re
import unittest

test_dir = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.dirname(test_dir) + os.sep + 'scripts'
data_dir = os.path.dirname(test_dir) + os.sep + 'data'
sys.path.insert(1, script_dir)

from highz_galaxy_catalog_io import HighzGalaxyCatalogIO


class TestClass(unittest.TestCase):

    def test_1(self):
        HighzGalaxyCatalogIO(catalog_meta_file = data_dir + os.sep + 'catalog_meta_info' + os.sep + 'Wisnioski_2019_KMOS3D_meta_info.ini')

    def test_2(self):
        HighzGalaxyCatalogIO(catalog_meta_file = data_dir + os.sep + 'catalog_meta_info' + os.sep + 'Johnson_2018_KROSS_meta_info.ini')


if __name__ == '__main__':
    unittest.main()


