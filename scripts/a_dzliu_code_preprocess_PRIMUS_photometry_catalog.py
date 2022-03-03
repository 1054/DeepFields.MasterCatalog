#!/usr/bin/env python
# 
import os, sys, re
import numpy as np
from astropy.table import Table
import astropy.units as u
from tqdm import tqdm


# Data file "PRIMUS_2013_photo_v1.fits.gz"
# is downloaded from 
# -- https://primus.ucsd.edu/version1.html


if not os.path.isfile('PRIMUS_2013_photo_v1_dzliu.fits'):
    tb = Table.read('PRIMUS_2013_photo_v1.fits.gz')
    filter_list_column = tb['FILTERLIST'].data
    mag_column = tb['MAG'].data
    magerr_column = tb['MAGERR'].data

    filter_mag_dict = {}
    filter_magerr_dict = {}
    row_counter = 0
    check_dup_filter_in_one_row = []
    print('looping rows')
    for i in tqdm(range(len(filter_list_column))):
        if i == 0:
            print('type(filter_list_column[i])', type(filter_list_column[i]))
            print('type(mag_column[i])', type(mag_column[i]))
            print('type(magerr_column[i])', type(magerr_column[i]))
            print('filter_list_column[i]', filter_list_column[i])
            print('mag_column[i]', mag_column[i])
            print('magerr_column[i]', magerr_column[i])
        #filter_list_x = [t.replace('.par','').replace('epsi_','') for t in filter_list_column[i].split()]
        filter_list_x = [t.decode().strip().replace('.par','').replace('epsi_','') for t in filter_list_column[i]]
        if i == 0:
            print('filter_list_x', filter_list_x)
        #mag_x = np.array(re.sub(r'^\((.*)\)$', r'\1', mag_column[i]).split()).astype(float)
        #magerr_x = np.array(re.sub(r'^\((.*)\)$', r'\1', magerr_column[i]).split()).astype(float)
        mag_x = mag_column[i].astype(float)
        magerr_x = magerr_column[i].astype(float)
        check_dup_filter_in_one_row = [] # we do not allow duplicate key in each row
        for j in tqdm(range(len(filter_list_x)), leave=False):
            key = filter_list_x[j]
            if key in check_dup_filter_in_one_row:
                raise Exception('Duplicate key in row %i! filter_list_x: %s'%(i, filter_list_x))
            if key not in filter_mag_dict:
                if row_counter>0:
                    filter_mag_dict[key] = [np.nan]*row_counter
                    filter_magerr_dict[key] = [np.nan]*row_counter
                else:
                    filter_mag_dict[key] = []
                    filter_magerr_dict[key] = []
            filter_mag_dict[key].append(mag_x[j])
            filter_magerr_dict[key].append(magerr_x[j])
            check_dup_filter_in_one_row.append(key)
        row_counter += 1

    for key in filter_mag_dict:
        print("tb[%r]"%('MAG_'+key))
        tb['MAG_'+key] = filter_mag_dict[key]
        tb['MAGERR_'+key] = filter_magerr_dict[key]

    tb.write('PRIMUS_2013_photo_v1_dzliu.fits', overwrite=True)



tb = Table.read('PRIMUS_2013_photo_v1_dzliu.fits')


# check capak_
tb.rename_column('MAG_subaru_suprimecam_Rc', 'MAG_subaru_suprimecam_r')
tb.rename_column('MAGERR_subaru_suprimecam_Rc', 'MAGERR_subaru_suprimecam_r')
tb['MAG_subaru_suprimecam_g'] = np.full(len(tb),fill_value=-99,dtype=float)
tb['MAGERR_subaru_suprimecam_g'] = np.full(len(tb),fill_value=-99,dtype=float)
for i in tqdm(range(len(tb))):
    for key, replacekey in list(zip(\
            ['subaru_suprimecam_B', 'subaru_suprimecam_V', 'subaru_suprimecam_g', 'subaru_suprimecam_r', 'subaru_suprimecam_i', 'subaru_suprimecam_z'],
            ['capak_subaru_suprimecam_B', 'capak_subaru_suprimecam_V', 'capak_subaru_suprimecam_g', 'capak_subaru_suprimecam_r', 'capak_subaru_suprimecam_i', 'capak_subaru_suprimecam_z'])):
        if tb['MAG_'+replacekey][i] > 0 and tb['MAG_'+key][i] > 0:
            raise Exception('Warning! Row %d has both valid MAG_capak_%s and MAG_%s!'%(i, key, key))
        elif tb['MAG_'+replacekey][i] > 0:
            tb['MAG_'+key][i] = tb['MAG_'+replacekey][i]
            tb['MAGERR_'+key][i] = tb['MAGERR_'+replacekey][i]
tb.remove_columns(['MAG_'+t for t in ['capak_subaru_suprimecam_B', 'capak_subaru_suprimecam_V', 'capak_subaru_suprimecam_g', 'capak_subaru_suprimecam_r', 'capak_subaru_suprimecam_i', 'capak_subaru_suprimecam_z']])
tb.remove_columns(['MAGERR_'+t for t in ['capak_subaru_suprimecam_B', 'capak_subaru_suprimecam_V', 'capak_subaru_suprimecam_g', 'capak_subaru_suprimecam_r', 'capak_subaru_suprimecam_i', 'capak_subaru_suprimecam_z']])

for col in tb.colnames:
    if col.startswith('MAG_'):
        key = re.sub(r'^MAG_', r'', col)
        mask = np.logical_or.reduce((tb['MAG_'+key]<=0.0, np.isnan(tb['MAG_'+key]), ~np.isfinite(tb['MAG_'+key])))
        tb['MAG_'+key][mask] = np.nan
        tb['MAGERR_'+key][mask] = np.nan

tb.write('PRIMUS_2013_photo_v1_dzliu_fixed.fits', overwrite=True)
print('Output to "%s"'%('PRIMUS_2013_photo_v1_dzliu_fixed.fits'))




