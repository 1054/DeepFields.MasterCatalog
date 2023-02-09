#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code will output "master_catalog_multi_entries.txt".
# Reference: D. Liu et al. 2019a, ApJS, 244, 40
import os, sys, re, copy, json, shutil, glob, gzip, time, random
sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
#from cds_catalog_io import CDSCatalogIO
#from fits_catalog_io import FITSCatalogIO
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))+os.sep+'scripts')
from highz_galaxy_catalog_io import HighzGalaxyCatalogIO as CatalogIO
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

# 
# set overwrite
overwrite = False
if len(sys.argv) > 1:
    for i in range(1,len(sys.argv)):
        if re.match(r'^[-]*overwrite$', sys.argv[i]):
            overwrite = True


# 
# set verbose
verbose = False
#verbose = True # for debugging


# 
# get repo_dir
repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print('repo_dir: %r'%(repo_dir))


# 
# get current_dir
current_dir = os.getcwd()
print('current_dir: %r'%(current_dir))


# 
# set catalog_cache_pool dir
if os.path.isdir('/data/catalogs'):
    catalog_cache_pool = '/data/catalogs'
else:
    catalog_cache_pool = None
print('catalog_cache_pool: %r'%(catalog_cache_pool))


# 
# check output file
Output_File = 'master_catalog_single_entry_more_columns.fits'
Output_Format = 'fits'
Output_Dict = OrderedDict()
if os.path.isfile(Output_File) and not overwrite:
    print('Found existing file "%s". Stopping. To overwrite, add -overwrite in the command line.'%(Output_File))


# 
# read 'master_catalog_multi_entries.json' and 'master_catalog_multi_entries.txt'
Input_File = 'master_catalog_multi_entries.fits'
Input_Json = 'master_catalog_multi_entries.json'
if not os.path.isfile(Input_Json):
    print('Error! File not found: "%s". Please run previous step first!'%(Input_Json))
    raise Exception('Error! File not found: "%s". Please run previous step first!'%(Input_Json))
print('Reading "%s"'%(Input_Json))
with open(Input_Json, 'r') as fp:
    Cat_Json_Dict = json.load(fp)

if not os.path.isfile(Input_File):
    print('Error! File not found: "%s". Please run previous step first!'%(Input_File))
    raise Exception('Error! File not found: "%s". Please run previous step first!'%(Input_File))
print('Reading "%s"'%(Input_File))
if Input_File.endswith('.txt'):
    MasterCat = Table.read(Input_File, format='ascii.commented_header')
else:
    MasterCat = Table.read(Input_File)


# 
# Concatenate columns
Cat_N = Cat_Json_Dict['CAT_N']
Cat_Index_2D = []
Cat_RA_2D = []
Cat_Dec_2D = []
Cat_Flag_2D = [] # Flag=0 means this catalog is the first entry of the source
Cat_Origin_2D = [] # origin catalog ID, 1-N
Cat_ID_2D = []
Cat_z_2D = []
Cat_zphot_2D = []
Cat_zspec_2D = []
Cat_Qzspec_2D = []
Cat_logMstar_2D = []
Cat_logSFR_2D = []
Cat_logSSFR_2D = []
Cat_Field_2D = []
Cat_Ref_Dict = OrderedDict()

for x in range(Cat_N):
    # concatenate mandatory columns
    Cat_Index_2D.append(MasterCat['Index_%d'%(x+1)].data)
    Cat_RA_2D.append(MasterCat['RA_%d'%(x+1)].data)
    Cat_Dec_2D.append(MasterCat['Dec_%d'%(x+1)].data)
    Cat_Flag_2D.append(MasterCat['Flag_%d'%(x+1)].data)
    Cat_Origin_2D.append(np.full(len(MasterCat), fill_value=x+1, dtype=np.int32))
    
    # read more columns from each catalog
    catalog_meta_info = Cat_Json_Dict['CAT_%d'%(x+1)]
    print('*-*-'*40)
    print('catalog_meta_info: %s'%(catalog_meta_info))
    
    Cat = CatalogIO(catalog_meta_info, catalog_cache_pool=catalog_cache_pool, verbose=verbose)
    
    if Cat.ID is None or Cat.RA is None or Cat.DEC is None:
        print('Error! Could not read ID RA Dec from table %s'%(catalog_meta_info))
        raise Exception('Error! Could not read ID RA Dec from table %s'%(catalog_meta_info))
    
    MasterCat_Index = MasterCat['Index_%d'%(x+1)].data
    MasterCat_argwhere = (np.arange(len(MasterCat)))[MasterCat_Index>=0]
    Cat_argwhere = MasterCat_Index[MasterCat_Index>=0]
    #intersect1d, MasterCat_argwhere, Cat_argwhere = np.intersect1d(MasterCat_ID, Cat.ID, return_indices=True) #<TODO># Cat.ID should not contain -99
    
    MasterCat_ID = np.full(len(MasterCat), fill_value='', dtype=object) # must use object for variable string length
    if Cat.ID is not None:
        MasterCat_ID[MasterCat_argwhere] = Cat.ID[Cat_argwhere].astype(object)
    Cat_ID_2D.append(MasterCat_ID)
    
    MasterCat_z = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
    if Cat.REDSHIFT is not None:
        MasterCat_z[MasterCat_argwhere] = Cat.REDSHIFT[Cat_argwhere]
    Cat_z_2D.append(MasterCat_z)
    
    MasterCat_zphot = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
    if Cat.ZPHOT is not None:
        MasterCat_zphot[MasterCat_argwhere] = Cat.ZPHOT[Cat_argwhere]
    Cat_zphot_2D.append(MasterCat_zphot)
    
    MasterCat_zspec = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
    if Cat.ZSPEC is not None:
        MasterCat_zspec[MasterCat_argwhere] = Cat.ZSPEC[Cat_argwhere]
    Cat_zspec_2D.append(MasterCat_zspec)
    
    MasterCat_Qzspec = np.full(len(MasterCat), fill_value='', dtype=object) # must use object for variable string length
    if Cat.QUALITY_ZSPEC is not None:
        MasterCat_Qzspec[MasterCat_argwhere] = Cat.QUALITY_ZSPEC[Cat_argwhere]
    Cat_Qzspec_2D.append(MasterCat_Qzspec)
    
    MasterCat_logMstar = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
    if Cat.LOGMSTAR is not None:
        MasterCat_logMstar[MasterCat_argwhere] = Cat.LOGMSTAR[Cat_argwhere]
    Cat_logMstar_2D.append(MasterCat_logMstar)
    
    MasterCat_logSFR = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
    if Cat.LOGSFR is not None:
        MasterCat_logSFR[MasterCat_argwhere] = Cat.LOGSFR[Cat_argwhere]
    Cat_logSFR_2D.append(MasterCat_logSFR)
    
    MasterCat_logSSFR = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
    if Cat.LOGSSFR is not None:
        MasterCat_logSSFR[MasterCat_argwhere] = Cat.LOGSSFR[Cat_argwhere]
    Cat_logSSFR_2D.append(MasterCat_logSSFR)
    
    MasterCat_Field = np.full(len(MasterCat), fill_value='', dtype=object) # must use object for variable string length
    if Cat.FIELD is not None:
        MasterCat_Field[MasterCat_argwhere] = Cat.FIELD[Cat_argwhere]
    else:
        if re.match(r'^.*_FIELD_(.*)_meta_info.ini$', os.path.basename(catalog_meta_info)):
            MasterCat_Field[:] = re.sub(r'^.*_FIELD_(.*)_meta_info.ini$', r'\1', os.path.basename(catalog_meta_info))
        elif re.match(r'^.*_COSMOS.*_meta_info.ini$', os.path.basename(catalog_meta_info)):
            MasterCat_Field[:] = 'COSMOS'
    Cat_Field_2D.append(MasterCat_Field)
    
    Cat_Ref_Dict[x+1] = Cat.ref
    
print('*-*-'*40)

Cat_Index_2D = np.array(Cat_Index_2D).astype(np.int64).T
Cat_ID_2D = np.array(Cat_ID_2D).T
Cat_RA_2D = np.array(Cat_RA_2D).astype(np.float64).T
Cat_Dec_2D = np.array(Cat_Dec_2D).astype(np.float64).T
Cat_Flag_2D = np.array(Cat_Flag_2D).astype(np.int64).T
Cat_Origin_2D = np.array(Cat_Origin_2D).astype(np.int32).T
Cat_z_2D = np.array(Cat_z_2D).astype(np.float32).T
Cat_zphot_2D = np.array(Cat_zphot_2D).astype(np.float32).T
Cat_zspec_2D = np.array(Cat_zspec_2D).astype(np.float32).T
Cat_Qzspec_2D = np.array(Cat_Qzspec_2D).T
Cat_logMstar_2D = np.array(Cat_logMstar_2D).astype(np.float32).T
Cat_logSFR_2D = np.array(Cat_logSFR_2D).astype(np.float32).T
Cat_logSSFR_2D = np.array(Cat_logSSFR_2D).astype(np.float32).T
Cat_Field_2D = np.array(Cat_Field_2D).T
print('Cat_ID_2D.shape', Cat_ID_2D.shape)
print('Cat_RA_2D.shape', Cat_RA_2D.shape)
print('Cat_Dec_2D.shape', Cat_Dec_2D.shape)
print('Cat_Flag_2D.shape', Cat_Flag_2D.shape)

# fix some redshifts
Cat_z_2D[Cat_z_2D>=99.] = np.nan
Cat_zphot_2D[Cat_zphot_2D>=99.] = np.nan
Cat_zspec_2D[Cat_zspec_2D>=99.] = np.nan
Cat_logMstar_2D[Cat_logMstar_2D>=99.] = np.nan
Cat_logSFR_2D[Cat_logSFR_2D>=99.] = np.nan
Cat_logSSFR_2D[Cat_logSSFR_2D>=99.] = np.nan

Cat_Mask_Valid_Entries_2D = np.logical_and(~np.isnan(Cat_Index_2D), Cat_Index_2D>=0)
Cat_Mask_First_Entry_2D = (Cat_Flag_2D==0) # because there is only one Flag=0 per row, so this mask returns an array with the same length as len(MasterCat)
Output_Dict['ID_Master'] = (np.arange(len(MasterCat))+1).astype(np.int64) # ID starts from 1. ID = Index + 1.
Output_Dict['RA_Master'] = Cat_RA_2D[Cat_Mask_First_Entry_2D].reshape(len(MasterCat))
Output_Dict['Dec_Master'] = Cat_Dec_2D[Cat_Mask_First_Entry_2D].reshape(len(MasterCat))
Output_Dict['Origin'] = Cat_Origin_2D[Cat_Mask_First_Entry_2D].reshape(len(MasterCat))
Output_Dict['ID_Origin'] = Cat_ID_2D[Cat_Mask_First_Entry_2D].reshape(len(MasterCat))
Output_Dict['Duplicate'] = np.count_nonzero(Cat_Flag_2D>=0, axis=-1).reshape(len(MasterCat))

Output_Dict['Field'] = Cat_Field_2D[Cat_Mask_First_Entry_2D].reshape(len(MasterCat))
#Output_Dict['Recognized_Field'] = DeepFieldDB.recognize_field_by_ra_dec() #<TODO>#

Output_Dict['z'] = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
Output_Dict['zphot'] = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
Output_Dict['zspec'] = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
Output_Dict['Qzspec'] = np.full(len(MasterCat), fill_value='', dtype=object)
Output_Dict['logMstar'] = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
Output_Dict['logSFR'] = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
Output_Dict['logSSFR'] = np.full(len(MasterCat), fill_value=np.nan, dtype=np.float32)
Output_Dict['Origin_z'] = np.full(len(MasterCat), fill_value=-99, dtype=np.int32)
Output_Dict['Origin_zphot'] = np.full(len(MasterCat), fill_value=-99, dtype=np.int32)
Output_Dict['Origin_zspec'] = np.full(len(MasterCat), fill_value=-99, dtype=np.int32)
Output_Dict['Origin_logMstar'] = np.full(len(MasterCat), fill_value=-99, dtype=np.int32)
Output_Dict['Origin_logSFR'] = np.full(len(MasterCat), fill_value=-99, dtype=np.int32)
Output_Dict['Origin_logSSFR'] = np.full(len(MasterCat), fill_value=-99, dtype=np.int32)
Output_Dict['zprior'] = ['']*len(MasterCat)
Output_Dict['N_zprior'] = [0]*len(MasterCat)
Output_Dict['Ref_zprior'] = ['']*len(MasterCat)
Output_Dict['Flag_inconsistent_zspec'] = np.full(len(MasterCat), fill_value=False, dtype=bool)
mask_valid_z = np.logical_and(~np.isnan(Cat_z_2D), Cat_z_2D>0.0)
mask_valid_zphot = np.logical_and(~np.isnan(Cat_zphot_2D), Cat_zphot_2D>0.0)
mask_valid_zspec = np.logical_and(~np.isnan(Cat_zspec_2D), Cat_zspec_2D>0.0)
mask_valid_Qzspec = np.array([re.match(r'^[1-9]+[0-9.]*$', t) for t in Cat_Qzspec_2D])
mask_valid_logMstar = np.logical_and(~np.isnan(Cat_logMstar_2D), Cat_logMstar_2D>0.0)
mask_valid_logSFR = np.logical_and(~np.isnan(Cat_logSFR_2D), Cat_logSFR_2D>-99.0)
mask_valid_logSSFR = np.logical_and(~np.isnan(Cat_logSSFR_2D), Cat_logSSFR_2D>-99.0)
print('Processing each row')
for i in tqdm(range(len(MasterCat))):
    for x in range(Cat_N):
        if mask_valid_z[i, x]:
            if np.isnan(Output_Dict['z'][i]):
                Output_Dict['z'][i] = Cat_z_2D[i, x]
                Output_Dict['Origin_z'][i] = x+1
            # 
            if Output_Dict['zprior'][i] == '':
                Output_Dict['zprior'][i] = '%s'%(Cat_z_2D[i, x])
                Output_Dict['Ref_zprior'][i] = '%s'%(Cat_Ref_Dict[x+1])
                Output_Dict['N_zprior'][i] = 1
            else:
                Output_Dict['zprior'][i] += ', %s'%(Cat_z_2D[i, x])
                Output_Dict['Ref_zprior'][i] += ', %s'%(Cat_Ref_Dict[x+1])
                Output_Dict['N_zprior'][i] += 1
        # 
        if mask_valid_zspec[i, x]:
            if np.isnan(Output_Dict['zspec'][i]) or \
               (mask_valid_Qzspec[i, x] and re.match(r'^[1-9]+[0-9.]*$', Output_Dict['Qzspec'][i]) is None): # force update first valid Qzspec
                Output_Dict['zspec'][i] = Cat_zspec_2D[i, x]
                Output_Dict['Origin_zspec'][i] = x+1
                # 
                Output_Dict['Qzspec'][i] = Cat_Qzspec_2D[i, x]
            # 
            if Output_Dict['zprior'][i] == '':
                Output_Dict['zprior'][i] = '%s'%(Cat_zspec_2D[i, x])
                Output_Dict['Ref_zprior'][i] = '%s(zspec)'%(Cat_Ref_Dict[x+1])
                Output_Dict['N_zprior'][i] = 1
            else:
                Output_Dict['zprior'][i] += ', %s'%(Cat_zspec_2D[i, x])
                Output_Dict['Ref_zprior'][i] += ', %s(zspec)'%(Cat_Ref_Dict[x+1])
                Output_Dict['N_zprior'][i] += 1
        # 
        if mask_valid_logMstar[i, x]:
            if np.isnan(Output_Dict['logMstar'][i]):
                Output_Dict['logMstar'][i] = Cat_logMstar_2D[i, x]
                Output_Dict['Origin_logMstar'][i] = x+1
        # 
        if mask_valid_logSFR[i, x]:
            if np.isnan(Output_Dict['logSFR'][i]):
                Output_Dict['logSFR'][i] = Cat_logSFR_2D[i, x]
                Output_Dict['Origin_logSFR'][i] = x+1
        # 
        if mask_valid_logSSFR[i, x]:
            if np.isnan(Output_Dict['logSSFR'][i]):
                Output_Dict['logSSFR'][i] = Cat_logSSFR_2D[i, x]
                Output_Dict['Origin_logSSFR'][i] = x+1
    
    # check Flags
    if Output_Dict['N_zprior'][i] >= 2:
        if Output_Dict['Ref_zprior'][i].count('(zspec)') >= 2:
            temp_zspec_list = []
            temp_zprior_list = Output_Dict['zprior'][i].split(',')
            temp_ref_zprior_list = Output_Dict['Ref_zprior'][i].split(',')
            for k in range(len(temp_ref_zprior_list)):
                if temp_ref_zprior_list[k].find('(zspec)') >= 0:
                    temp_zspec_list.append(float(temp_zprior_list[k]))
            if len(temp_zspec_list) >= 2:
                if not np.all(np.isclose(np.diff(np.array(temp_zspec_list)), 0.0, atol=0.05*np.max(np.array(temp_zprior_list).astype(float)))):
                    #<TODO># relative difference for inconsistent zspec: 0.05
                    # note that because the compared value is 0.0, rtol takes not effect.
                    Output_Dict['Flag_inconsistent_zspec'][i] = True


# check
for key in Output_Dict:
    if isinstance(Output_Dict[key], list):
        Output_Dict[key] = np.array(Output_Dict[key])
    print('Output_Dict[%r].shape'%(key), Output_Dict[key].shape)


# make table and fix object col
Output_Table = Table(Output_Dict)
for col in Output_Table.colnames:
    if Output_Table[col].dtype == object:
        print('Converting column %r dtype from object to %r'%(col, 'str'))
        Output_Table[col] = Output_Table[col].astype(str)


# Output
print('Writing table to disk')
if os.path.isfile(Output_File):
    shutil.move(Output_File, Output_File+'.backup')
Output_Table.write(Output_File, format=Output_Format)
print('Output to "%s"'%(Output_File))


# Compress file with gzip
print('Compressing table on disk')
if os.path.isfile(Output_File+'.gz'):
    shutil.move(Output_File+'.gz', Output_File+'.gz'+'.backup')
with open(Output_File, 'rb') as f_in:
    with gzip.open(Output_File+'.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
print('Output to "%s"'%(Output_File+'.gz'))







