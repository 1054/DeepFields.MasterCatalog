#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# This code will output "master_catalog_multi_entries.txt"
# Reference: D. Liu et al. 2019a, ApJS, 244, 40
import os, sys, re, copy, json, shutil, glob, time, random
sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
#from cds_catalog_io import CDSCatalogIO
#from fits_catalog_io import FITSCatalogIO
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))+os.sep+'scripts')
from highz_galaxy_catalog_io import HighzGalaxyCatalogIO as CatalogIO
from collections import OrderedDict
from distutils.version import LooseVersion
import numpy as np
from astropy.table import Table
from scipy import spatial
from scipy.spatial import KDTree
from tqdm import tqdm
import configparser
class CaseConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

# 
# set const
separation_limit = 1.0
verbose = False
#verbose = True # for debugging


# 
# set overwrite
overwrite = False
if len(sys.argv) > 1:
    for i in range(1,len(sys.argv)):
        if re.match(r'^[-]*overwrite$', sys.argv[i]):
            overwrite = True
            print('overwrite = True')
            break


# 
# set dryrun
dryrun = False
if len(sys.argv) > 1:
    for i in range(1,len(sys.argv)):
        if re.match(r'^[-]*dry(-|)run$', sys.argv[i]):
            dryrun = True
            print('dryrun = True')
            break


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
print('catalog_cache_root: %r'%(catalog_cache_pool))


# 
# find catalog meta infos (maintain certain order)
list_of_catalog_meta_info = [
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Weaver_2021_COSMOS2020_CLASSIC_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Weaver_2021_COSMOS2020_FARMER_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Laigle_2016_COSMOS2015_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Muzzin_2013_UltraVISTA_FIELD_COSMOS_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Skelton_2014_3D-HST_FIELD_COSMOS_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Skelton_2014_3D-HST_FIELD_EGS_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Skelton_2014_3D-HST_FIELD_GOODSN_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Skelton_2014_3D-HST_FIELD_GOODSS_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Skelton_2014_3D-HST_FIELD_UDS_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Momcheva_2016_3D-HST_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Straatman_2016_ZFOURGE_FIELD_COSMOS_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Straatman_2016_ZFOURGE_FIELD_CDFS_meta_info.ini'),
os.path.join(repo_dir, 'data', 'catalog_meta_info', 'Straatman_2016_ZFOURGE_FIELD_UDS_meta_info.ini'),
]
list_of_catalog_meta_info2 = glob.glob(os.path.join(repo_dir, 'data', 'catalog_meta_info', '*.ini'))
list_of_catalog_meta_info_year2 = [int(re.sub(r'^([a-zA-Z]+)_([0-9]+)_.*', r'\2', os.path.basename(t))) for t in list_of_catalog_meta_info2]
list_of_catalog_meta_info_lead2 = [re.sub(r'^([a-zA-Z]+)_([0-9]+)_.*', r'\1', os.path.basename(t)) for t in list_of_catalog_meta_info2]
paired = zip(list_of_catalog_meta_info_year2, list_of_catalog_meta_info_lead2, list_of_catalog_meta_info2)
paired_sorted = sorted(paired)
list_of_catalog_meta_info_year2, list_of_catalog_meta_info_lead2, list_of_catalog_meta_info2 = zip(*paired_sorted)
for catalog_meta_info in list_of_catalog_meta_info2:
    if catalog_meta_info not in list_of_catalog_meta_info:
        list_of_catalog_meta_info.append(catalog_meta_info)

Cat_N = len(list_of_catalog_meta_info)

Cat_Json_Dict = OrderedDict()
Cat_Json_Dict['CAT_N'] = Cat_N

for x in range(Cat_N):
    catalog_meta_info = list_of_catalog_meta_info[x]
    print('*-*-'*40)
    print('catalog_meta_info: %s'%(catalog_meta_info))
    
    #if not (catalog_meta_info.find('Lilly_2007')>=0):
    #    continue
    
    #<DEBUG>#
    #iniparser = CaseConfigParser()
    #iniparser.read(catalog_meta_info)
    #print('iniparser[\'COLUMNS\']', list(iniparser['COLUMNS'].keys()))
    
    #<DEBUG>#
    #if 'QUERY_COMMAND' in iniparser['CDS']:
    #    query_command = iniparser['CDS']['QUERY_COMMAND']
    #    print('query_command', query_command)
    #    raise NotImplementedError()
    #continue
    
    Cat = CatalogIO(catalog_meta_info, catalog_cache_pool=catalog_cache_pool, verbose=verbose)
    
    #<DEBUG>#
    #print('Cat.iniparser._sections.items()', Cat.iniparser._sections.items())
    #print("Cat.iniparser['POSTPROCESSING']._options()", Cat.iniparser['POSTPROCESSING']._options())
    #for col in Cat.iniparser['POSTPROCESSING']:
    #    print('col:', col, 'value:', Cat.iniparser['POSTPROCESSING'][col])
    
    if Cat.ID is None or Cat.RA is None or Cat.DEC is None:
        print('Error! Could not read ID RA Dec from table %s'%(catalog_meta_info))
        raise Exception('Error! Could not read ID RA Dec from table %s'%(catalog_meta_info))
    
    #raise NotImplementedError()
    
    #time.sleep(random.randint(5,30))
    
    if 'ASTROMETRY' in Cat.iniparser:
        if 'RA_CORRECTION_FUNCTION' in Cat.iniparser['ASTROMETRY']:
            print('Astrometry correction for RA: ', Cat.iniparser['ASTROMETRY']['RA_CORRECTION_FUNCTION'])
            RA_correction_function = eval(Cat.iniparser['ASTROMETRY']['RA_CORRECTION_FUNCTION'])
            Cat.RA = RA_correction_function(Cat.RA, Cat.DEC)
        if 'DEC_CORRECTION_FUNCTION' in Cat.iniparser['ASTROMETRY']:
            print('Astrometry correction for DEC: ', Cat.iniparser['ASTROMETRY']['DEC_CORRECTION_FUNCTION'])
            DEC_correction_function = eval(Cat.iniparser['ASTROMETRY']['DEC_CORRECTION_FUNCTION'])
            Cat.DEC = DEC_correction_function(Cat.RA, Cat.DEC)
    
    #print('Cat.ID.dtype', Cat.ID.dtype)
    #if Cat.ID.dtype.char == 'S':
    #    globals()['ID_%d'%(x+1)] = (np.arange(len(Cat.ID))+1).astype(np.int64)
    #else:
    #    globals()['ID_%d'%(x+1)] = copy.copy(Cat.ID)
    globals()['ID_%d'%(x+1)] = (np.arange(len(Cat.ID))).astype(int)   # now we use index instead of some ID in the catalog
    #globals()['ID_%d'%(x+1)] = Cat.ID
    globals()['RA_%d'%(x+1)] = Cat.RA
    globals()['Dec_%d'%(x+1)] = Cat.DEC
    globals()['Flag_%d'%(x+1)] = np.full(len(Cat.ID), fill_value=0, dtype=int)
    
    Cat_Json_Dict['CAT_%d'%(x+1)] = catalog_meta_info


#raise NotImplementedError() # for debugging
if dryrun:
    print('In dry run mode! Stop here.')
    sys.exit()


if len(Cat_Json_Dict) <= 1:
    raise Exception('No enough catalog!')



# 
# Define output global variables
#for x in range(Cat_N):
#    globals()['Flag_%d'%(x+1)] = (globals()['RA_%d'%(x+1)]*0).astype(int)
#    #globals()['Output_ID_%d'%(x+1)] = -99
#    #globals()['Output_RA_%d'%(x+1)] = -99.0
#    #globals()['Output_Dec_%d'%(x+1)] = -99.0
#    #globals()['Output_Flag_%d'%(x+1)] = -99



# 
# Define output catalog file
Output_File = 'master_catalog_multi_entries.fits'
Output_Json = 'master_catalog_multi_entries.json'

if os.path.isfile(Output_File):
    if overwrite: 
        shutil.move(Output_File, Output_File+'.backup')
    else:
        print('Found existing file "%s". Stopping. To overwrite, add -overwrite in the command line.'%(Output_File))
        sys.exit()

if os.path.isfile(Output_Json):
    if overwrite:
        shutil.move(Output_Json, Output_Json+'.backup')
with open(Output_Json, 'w') as fp:
    json.dump(Cat_Json_Dict, fp, indent=4)

#Output_fp = open(Output_File, 'w')



# 
# Define loop variables
Total_Obj = 0
Count_Obj = 0
Count_Dump = 0
Debug_level = 1



# 
# Loop each catalog to make KDTree
for x in range(Cat_N):
    print('Making KDTree for Table %d'%(x+1))
    globals()['RADec_%d'%(x+1)] = np.column_stack((globals()['RA_%d'%(x+1)]*np.cos(globals()['Dec_%d'%(x+1)]/180.0*np.pi), globals()['Dec_%d'%(x+1)]))
    globals()['KDTree_%d'%(x+1)] = KDTree(globals()['RADec_%d'%(x+1)])
    # 
    # Total_Obj
    Total_Obj = Total_Obj + len(globals()['ID_%d'%(x+1)])
    # 
    # Closest_Pairs
    #closest_pairs = (globals()['KDTree_%d'%(x+1)]).query_pairs(0.75/3600.0) # within 0.75 arcsec
    #closest_distances = []
    #for closest_pair in closest_pairs:
    #    RADec_x = (globals()['RADec_%d'%(x+1)])[closest_pair[0]] 
    #    RADec_y = (globals()['RADec_%d'%(x+1)])[closest_pair[1]] 
    #    closest_distances.append(np.sqrt((RADec_x[0]-RADec_y[0])**2 + (RADec_x[1]-RADec_y[1])**2) * 3600.0)
    #closest_pair_index = (np.argsort(closest_distances))[0]
    #print('The closest pair separation in Table %d is %.10f arcsec (pair object indexes %d and %d)'%(x+1,closest_distances[closest_pair_index],list(closest_pairs)[closest_pair_index][0],list(closest_pairs)[closest_pair_index][1]))


print("Total_Obj: %d"%(Total_Obj))
print("")


# 
# Prepare output file header
#Output_header_fmt = ''
#Output_header_var = []
#Output_data_fmt = ''
#Output_data_var = []
#for x in range(Cat_N):
#    # 
#    if x == 0:
#        Output_header_fmt = '# %13s %15s %15s %15s'
#    else:
#        Output_header_fmt = Output_header_fmt + ' %15s %15s %15s %15s'
#    # 
#    if x == Cat_N-1:
#        Output_header_fmt = Output_header_fmt + '\n'
#    # 
#    Output_header_var.append('ID_%d'%(x+1))
#    Output_header_var.append('RA_%d'%(x+1))
#    Output_header_var.append('Dec_%d'%(x+1))
#    Output_header_var.append('Flag_%d'%(x+1))
## 
#Output_fp.write(Output_header_fmt%tuple(Output_header_var))


# 
# Prepare output array
Output_ID_Array = None
Output_RA_Array = None
Output_Dec_Array = None
Output_Flag_Array = None


# 
# Loop each input catalog
for x in tqdm(range(Cat_N)):
    # 
    # Select catalog x
    print('')
    print('Cross-matching objects in Table %d'%(x+1))
    ID_x = globals()['ID_%d'%(x+1)]
    RA_x = globals()['RA_%d'%(x+1)]
    Dec_x = globals()['Dec_%d'%(x+1)]
    Flag_x = globals()['Flag_%d'%(x+1)]
    RADec_x = globals()['RADec_%d'%(x+1)]
    KDTree_x = globals()['KDTree_%d'%(x+1)]
    # 
    # Prepare master catalog row
    OneCat_ID_Array = np.full((len(ID_x), Cat_N), fill_value=-99, dtype=int) # 4 columns IDX,RA,DEC,FLAG for each input catalog
    OneCat_RA_Array = np.full((len(ID_x), Cat_N), fill_value=-99, dtype=float) # 4 columns IDX,RA,DEC,FLAG for each input catalog
    OneCat_Dec_Array = np.full((len(ID_x), Cat_N), fill_value=-99, dtype=float) # 4 columns IDX,RA,DEC,FLAG for each input catalog
    OneCat_Flag_Array = np.full((len(ID_x), Cat_N), fill_value=-99, dtype=int) # 4 columns IDX,RA,DEC,FLAG for each input catalog
    print('OneCat_ID_Array.shape', OneCat_ID_Array.shape)
    # 
    # Loop each object in catalog x
    for j in tqdm(range(len(ID_x)), leave=False):
        # 
        # Count_Obj
        Count_Obj = Count_Obj + 1
        # 
        # Print progress
        #if Debug_level >= 1:
        #    if j == 0:
        #        sys.stdout.write('%0.0f%%'%(float(Count_Obj)/(Total_Obj/100.0)))
        #        sys.stdout.flush()
        #    elif ((Count_Obj)%(Total_Obj/100)) == 0:
        #        sys.stdout.write(' %0.0f%%'%(float(Count_Obj)/(Total_Obj/100.0)))
        #        sys.stdout.flush()
        #    if j == len(ID_x)-1:
        #        sys.stdout.write('\n')
        #        sys.stdout.flush()
        # 
        # <DONE><20170426><DEBUG>
        #if ID_x[j] != 477498:
        #    continue
        #else:
        #    print("DEBUG: Checking by eye: Laigle ID 477498, Muzzin ID 106037, Capak ID 1298171, Smolcic ID 8595")
        #    # checked OK! The code can reproduce this match!
        # 
        # Skip flagged object
        if Flag_x[j] > 0:
            continue
        # 
        # Prepare output variables
        #for y in range(Cat_N):
        #    globals()['Output_ID_%d'%(y+1)] = -99
        #    globals()['Output_RA_%d'%(y+1)] = -99.0
        #    globals()['Output_Dec_%d'%(y+1)] = -99.0
        #    globals()['Output_Flag_%d'%(y+1)] = -99
        # 
        # do cross-match for each object in catalog x to each catalog y
        for y in range(Cat_N):
            # 
            # skip itself
            #if y == x:
            #    continue
            # 
            # cross-match x to y
            ID_y = globals()['ID_%d'%(y+1)]
            RA_y = globals()['RA_%d'%(y+1)]
            Dec_y = globals()['Dec_%d'%(y+1)]
            RADec_y = globals()['RADec_%d'%(y+1)]
            KDTree_y = globals()['KDTree_%d'%(y+1)]
            distance_forward, index_forward = KDTree_y.query(RADec_x[j], k=10, distance_upper_bound=1.0/3600.0)
            distance_forward = distance_forward * 3600.0
            # 
            # skip if no valid cross-match
            if np.isnan(distance_forward[0]) == True or distance_forward[0] > separation_limit:
                continue
            # 
            # found a cross-match, print the matched counterpart
            if Debug_level >= 2:
                print('%15s %s'%(' ', 'Found matched Table %d index %d to Table %d index %d'%(y+1,index_forward[0],x+1,j)))
            # 
            # reversed-cross-match y to x
            distance_backward, index_backward = KDTree_x.query(RADec_y[index_forward[0]], k=10, distance_upper_bound=1.0/3600.0)
            distance_backward = distance_backward * 3600.0
            # 
            # skip if no valid reversed-cross-match
            if np.isnan(distance_backward[0]) == True or distance_backward[0] > separation_limit:
                continue
            # 
            # if the cross-match and reversed-cross-match agree
            if index_backward[0] == j:
                # 
                # mark as matched! store results!
                if True:
                    #(globals()['Output_ID_%d'%(x+1)])  = (ID_x[index_backward[0]])
                    #(globals()['Output_RA_%d'%(x+1)])  = (RA_x[index_backward[0]])
                    #(globals()['Output_Dec_%d'%(x+1)]) = (Dec_x[index_backward[0]])
                    #(globals()['Output_Flag_%d'%(x+1)]) = 0
                    OneCat_ID_Array[j, x]  = ID_x[index_backward[0]]
                    OneCat_RA_Array[j, x]  = RA_x[index_backward[0]]
                    OneCat_Dec_Array[j, x] = Dec_x[index_backward[0]]
                    OneCat_Flag_Array[j, x] = 0
                    #print('OneCat_Flag_Array[%d, %d]'%(j, x), OneCat_Flag_Array[j, x])
                if y != x:
                    #(globals()['Output_ID_%d'%(y+1)])  = (ID_y[index_forward[0]])
                    #(globals()['Output_RA_%d'%(y+1)])  = (RA_y[index_forward[0]])
                    #(globals()['Output_Dec_%d'%(y+1)]) = (Dec_y[index_forward[0]])
                    #(globals()['Output_Flag_%d'%(y+1)]) = 1
                    OneCat_ID_Array[j, y]  = ID_y[index_forward[0]]
                    OneCat_RA_Array[j, y]  = RA_y[index_forward[0]]
                    OneCat_Dec_Array[j, y] = Dec_y[index_forward[0]]
                    OneCat_Flag_Array[j, y] = 1
                    #print('OneCat_Flag_Array[%d, %d]'%(j, y), OneCat_Flag_Array[j, y])
                if True:
                    (globals()['Flag_%d'%(y+1)])[index_forward[0]] = 1
        # 
        # Prepare output data var list
        #Output_data_fmt = ''
        #Output_data_var = []
        #for y in range(Cat_N):
        #    Output_data_var.append(globals()['Output_ID_%d'%(y+1)])
        #    Output_data_var.append(globals()['Output_RA_%d'%(y+1)])
        #    Output_data_var.append(globals()['Output_Dec_%d'%(y+1)])
        #    Output_data_var.append(globals()['Output_Flag_%d'%(y+1)])
        #    # 
        #    if globals()['Output_ID_%d'%(y+1)] > -99:
        #        if y == 0:
        #            Output_data_fmt = '%15d %15.10f %15.10f %15d'
        #        else:
        #            Output_data_fmt = Output_data_fmt + ' %15d %15.10f %15.10f %15d'
        #    else:
        #        if y == 0:
        #            Output_data_fmt = '%15d %15.0f %15.0f %15d'
        #        else:
        #            Output_data_fmt = Output_data_fmt + ' %15d %15.0f %15.0f %15d'
        #    # 
        #    if y == Cat_N-1:
        #        Output_data_fmt = Output_data_fmt + '\n'
        # 
        # Output 
        #Output_fp.write(Output_data_fmt%tuple(Output_data_var))
        # 
        # Dump table
        if Debug_level >= 1:
            if Count_Obj > 2 and Count_Obj%int(np.round(Total_Obj/10.)) == 0 and Count_Obj < Total_Obj-2:
                print('')
                print('Dumping working table ...')
                Count_Dump += 1
                OneCat_Mask = (OneCat_Flag_Array[:, x]==0)
                if Output_ID_Array is None:
                    Dump_ID_Array = OneCat_ID_Array[OneCat_Mask, :]
                    Dump_RA_Array = OneCat_RA_Array[OneCat_Mask, :]
                    Dump_Dec_Array = OneCat_Dec_Array[OneCat_Mask, :]
                    Dump_Flag_Array = OneCat_Flag_Array[OneCat_Mask, :]
                else:
                    Dump_ID_Array = np.concatenate([Output_ID_Array, OneCat_ID_Array[OneCat_Mask, :]], axis=0)
                    Dump_RA_Array = np.concatenate([Output_RA_Array, OneCat_RA_Array[OneCat_Mask, :]], axis=0)
                    Dump_Dec_Array = np.concatenate([Output_Dec_Array, OneCat_Dec_Array[OneCat_Mask, :]], axis=0)
                    Dump_Flag_Array = np.concatenate([Output_Flag_Array, OneCat_Flag_Array[OneCat_Mask, :]], axis=0)
                # 
                Dump_Table = Table()
                for tempx in range(Cat_N):
                    Dump_Table.add_column(Dump_ID_Array[:, tempx], name='Index_%d'%(tempx+1))
                    Dump_Table.add_column(Dump_RA_Array[:, tempx], name='RA_%d'%(tempx+1))
                    Dump_Table.add_column(Dump_Dec_Array[:, tempx], name='Dec_%d'%(tempx+1))
                    Dump_Table.add_column(Dump_Flag_Array[:, tempx], name='Flag_%d'%(tempx+1))
                Dump_Table.write('Dump_Table_%d.fits'%(Count_Dump), format='fits', overwrite=True)
                print('Dumped working table as "%s"'%('Dump_Table_%d.fits'%(Count_Dump)))
                #raise NotImplementedError()
        # 
        # 
        #pass
        #break
    # 
    # Append to output array
    OneCat_Mask = (OneCat_Flag_Array[:, x]==0)
    if Output_ID_Array is None:
        Output_ID_Array = OneCat_ID_Array[OneCat_Mask, :]
        Output_RA_Array = OneCat_RA_Array[OneCat_Mask, :]
        Output_Dec_Array = OneCat_Dec_Array[OneCat_Mask, :]
        Output_Flag_Array = OneCat_Flag_Array[OneCat_Mask, :]
    else:
        Output_ID_Array = np.concatenate([Output_ID_Array, OneCat_ID_Array[OneCat_Mask, :]], axis=0)
        Output_RA_Array = np.concatenate([Output_RA_Array, OneCat_RA_Array[OneCat_Mask, :]], axis=0)
        Output_Dec_Array = np.concatenate([Output_Dec_Array, OneCat_Dec_Array[OneCat_Mask, :]], axis=0)
        Output_Flag_Array = np.concatenate([Output_Flag_Array, OneCat_Flag_Array[OneCat_Mask, :]], axis=0)
    # 
    # 
    #pass
    #break


#Output_fp.close()


print('')
print('Making output table')
Output_Table = Table()
for x in tqdm(range(Cat_N)):
    Output_Table.add_column(Output_ID_Array[:, x], name='Index_%d'%(x+1))
    Output_Table.add_column(Output_RA_Array[:, x], name='RA_%d'%(x+1))
    Output_Table.add_column(Output_Dec_Array[:, x], name='Dec_%d'%(x+1))
    Output_Table.add_column(Output_Flag_Array[:, x], name='Flag_%d'%(x+1))
Output_Table.write(Output_File, format='fits')

print('Output to "%s"!'%(Output_File))





