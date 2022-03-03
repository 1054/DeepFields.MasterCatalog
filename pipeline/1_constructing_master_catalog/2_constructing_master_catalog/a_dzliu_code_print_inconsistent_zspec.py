#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# This code will output "master_catalog_multi_entries.txt"
import os, sys, re, copy, json, shutil, glob, gzip, time, random
sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
#from cds_catalog_io import CDSCatalogIO
#from fits_catalog_io import FITSCatalogIO
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))+os.sep+'scripts')
#from highz_galaxy_catalog_io import HighzGalaxyCatalogIO as CatalogIO
#from highz_deep_field_db import HighzDeepFieldDB as DeepFieldDB
from collections import OrderedDict
from distutils.version import LooseVersion
from astropy.table import Table
import numpy as np
#from scipy import spatial
#from scipy.spatial import KDTree
from tqdm import tqdm
#import configparser
#class CaseConfigParser(configparser.ConfigParser):
#    def optionxform(self, optionstr):
#        return optionstr



tb = Table.read('master_catalog_single_entry_more_columns_v20210601a.fits')

Flag_inconsistent_zspec = np.full(len(tb), fill_value=False, dtype=bool)
for i in tqdm(range(len(tb))):
    zspec_list = []
    if tb['zprior'][i].strip() != '':
        zprior_list = tb['zprior'][i].strip().split(',')
        Ref_zprior_list = tb['Ref_zprior'][i].strip().split(',')
        for k in range(len(Ref_zprior_list)):
            if Ref_zprior_list[k].find('zspec') >= 0:
                #try:
                #    float(zprior_list[k])
                #except:
                #    print('i', i)
                zspec_list.append(float(zprior_list[k]))
        if not np.all(np.isclose(np.diff(zspec_list), 0.0, rtol=0.05, atol=0.05)):
            Flag_inconsistent_zspec[i] = True

tb['Flag_inconsistent_zspec'] = Flag_inconsistent_zspec

tb.write('master_catalog_single_entry_more_columns_v20210601a_extracols.fits', overwrite=True)





