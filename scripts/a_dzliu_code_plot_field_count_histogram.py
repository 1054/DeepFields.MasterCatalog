#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
import numpy as np
from astropy.table import Table
import matplotlib as mpl
import matplotlib.pyplot as plt

tb = Table.read('master_catalog_single_entry_more_columns.fits')
out_name = 'Plot_field_count_histogram'


fig = plt.figure(figsize=(5.5, 4.0))
ax = fig.add_subplot(1, 1, 1)

tb['Qzspec'][tb['Qzspec']==''] = 'nan'
tb['Qzspec'] = tb['Qzspec'].astype(float)

tbgroupped = tb.group_by('Field')
field_list = []
count_list = []
field_count_dict = {}
field_count_zspec_dict = {}
for key, tbgroup in zip(tbgroupped.groups.keys, tbgroupped.groups):
    field = key['Field'].strip()
    if field == '':
        field = '[NoName]'
    count = len(tbgroup)
    print('Field: %s, len: %d'%(field, count))
    field_list.append(field)
    count_list.append(count)
    # 
    if field.startswith('candels-cdfs') or field.startswith('cdfs_swire') or field.startswith('ECDFS'): 
        field = 'CDFS'
    elif field.startswith('AEGIS'): 
        field = 'EGS'
    elif field.startswith('cosmos_'): 
        field = 'COSMOS'
    elif field.startswith('GOODS-N') or field.startswith('GOODSN'): 
        field = 'GOODS-N'
    elif field.startswith('GOODS-S') or field.startswith('GOODSS'): 
        field = 'GOODS-S'
    elif field.startswith('deep2_'): 
        field = 'DEEP2'
    elif field.startswith('es1_'): 
        field = 'ELIAS-S1'
    elif field.startswith('cfhtls_xmm'): 
        field = 'XMM-LSS'
    elif field.startswith('cfhtls_vvds'): 
        field = 'VVDS'
    elif field.startswith('xmm_swire'): 
        field = 'XMM-LSS'
    elif field.startswith('sdss_'): 
        field = 'SDSS'
    # 
    if field in field_count_dict:
        field_count_dict[field] += count
    else:
        field_count_dict[field] = count
    # 
    mask_zspec = np.logical_and(tbgroup['zspec']>0.0, tbgroup['Qzspec']>0.0)
    count_zspec = np.count_nonzero(mask_zspec)
    if count_zspec > 0:
        if field in field_count_zspec_dict:
            field_count_zspec_dict[field] += count_zspec
        else:
            field_count_zspec_dict[field] = count_zspec


field_list = []
count_list = []
count_zspec_list = []
for key in field_count_dict:
    field_list.append(key)
    count_list.append(field_count_dict[key])
    if key in field_count_zspec_dict:
        count_zspec_list.append(field_count_zspec_dict[key])
    else:
        count_zspec_list.append(np.nan)

ax.bar(np.arange(len(field_list)), count_list, width=0.9, align='center', color='C0', alpha=0.5, label='All z')
ax.bar(np.arange(len(field_list)), count_zspec_list, width=0.8, align='center', color='C1', alpha=0.5, label='zspec')

ax.set_yscale('log')
ax.set_ylabel('N', fontsize=12)
ax.tick_params(which='both', direction='in')
ax.set_xticks(np.arange(len(field_list)))
xticklabels = ax.set_xticklabels(field_list, rotation=80, ha='right', fontsize=9)
#for i, label in enumerate(xticklabels):
#    label.set_y(label.get_position()[1] - (i % 2) * 0.075)

ax.legend(fontsize=9)
ax.grid(True, color='#999999', ls='dotted', lw=0.25, alpha=0.25)


fig.tight_layout()


fig.savefig(out_name+'.pdf', dpi=300, transparent=True)
fig.savefig(out_name+'.png', dpi=300, transparent=True)
print('Output to "%s"'%(out_name+'.pdf'))
print('Output to "%s"'%(out_name+'.png'))

