#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
import numpy as np
from astropy.table import Table
import matplotlib as mpl
import matplotlib.pyplot as plt

tb = Table.read('master_catalog_single_entry_more_columns.fits')


tb['Qzspec'][tb['Qzspec']==''] = 'nan'
tb['Qzspec'] = tb['Qzspec'].astype(float)


mask_zspec = np.logical_and(tb['zspec']>0.0, tb['Qzspec']>0.0)
mask_zspec_GE_3 = np.logical_and(tb['zspec']>=3.0, tb['Qzspec']>0.0)


print('N_zspec:', np.count_nonzero(mask_zspec))
print('N_zspec_GE_3:', np.count_nonzero(mask_zspec_GE_3))

