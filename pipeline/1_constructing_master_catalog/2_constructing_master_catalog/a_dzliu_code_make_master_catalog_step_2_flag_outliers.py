#!/usr/bin/env python2.7
# 

import sys

from CrabFitsTable import CrabFitsTable
from astropy.table import Table

from scipy import spatial
from scipy.spatial import KDTree
import numpy




# 
# <TODO> User-input
Cat_1 = CrabFitsTable('../COSMOS2015_Laigle2016/COSMOS2015_Laigle+_v1.1_corrected_for_astrometry_by_dzliu_v20181107.fits')
ID_1 = Cat_1.getColumn('NUMBER')
RA_1 = Cat_1.getColumn('ALPHA_J2000')
Dec_1 = Cat_1.getColumn('DELTA_J2000')
Sep_1 = 1.0 # arcsec

Cat_2 = CrabFitsTable('Catalog_Muzzin_2013_UVISTA_final_v4.1.fits')
ID_2 = Cat_2.getColumn('id')
RA_2 = Cat_2.getColumn('ra')
Dec_2 = Cat_2.getColumn('dec')
Sep_2 = 1.0 # arcsec

Cat_3 = CrabFitsTable('Catalog_Capak_2007_reformatted_by_plang.fits')
ID_3 = Cat_3.getColumn('ID')
RA_3 = Cat_3.getColumn('RA')
Dec_3 = Cat_3.getColumn('DEC')
Sep_3 = 1.0 # arcsec

Cat_4 = CrabFitsTable('Catalog_Ashby_2018_SMUVS_all_combined_by_dzliu.fits')
ID_4 = Cat_4.getColumn('ID')
RA_4 = Cat_4.getColumn('ra')
Dec_4 = Cat_4.getColumn('dec')
Sep_4 = 1.0 # arcsec

Cat_5 = CrabFitsTable('Catalog_Davidzon_2017_IRAC_SPLASH_Residual_SExtractor.fits')
ID_5 = Cat_5.getColumn('ID')
RA_5 = Cat_5.getColumn('RA_IRAC_ch1')
Dec_5 = Cat_5.getColumn('Dec_IRAC_ch1')
Sep_5 = 1.0 # arcsec

Cat_6 = CrabFitsTable('Catalog_Smolcic_2017_vla3_cosmos_sources_160321_public5sig.fits')
ID_6 = Cat_6.getColumn('id')
RA_6 = Cat_6.getColumn('ra')
Dec_6 = Cat_6.getColumn('dec')
Sep_6 = 1.0 # arcsec

Cat_7 = CrabFitsTable('Catalog_Sanders_2007_SCosmos.fits') # IRAC
ID_7 = Cat_7.getColumn('ID')
RA_7 = Cat_7.getColumn('RA')
Dec_7 = Cat_7.getColumn('DEC')
Sep_7 = 1.0 # arcsec

Cat_8 = CrabFitsTable('Catalog_Le_Floch_2009_COSMOS_24um.fits') # MIPS24 GO3
ID_8 = Cat_8.getColumn('ID_MIPS24')
RA_8 = Cat_8.getColumn('RA_MIPS')
Dec_8 = Cat_8.getColumn('Dec_MIPS')
Sep_8 = 3.0 # arcsec

#Cat_9 = CrabFitsTable('Catalog_Le_Floch_2009_COSMOS_24um.fits') # MIPS24 GO2 deep & wide <TODO>
#ID_9 = Cat_9.getColumn('ID_MIPS24')
#RA_9 = Cat_9.getColumn('RA_MIPS')
#Dec_9 = Cat_9.getColumn('Dec_MIPS')
#Sep_9 = 3.0 # arcsec

Cat_N = 8

#print(Cat_1.getColumnNames())
#print(Cat_2.getColumnNames())
#print(Cat_3.getColumnNames())
#print(Cat_4.getColumnNames())
#print(Cat_5.getColumnNames())



# 
# <TODO> User-input
Output_column_sel = []
Output_column_sel.append({'Catalog': 1, 'Column': 'FLAG_PETER',     'ID': 'NUMBER', 'OutputName': 'Flag_Laigle_FLAG_PETER'      }) # 'OutputName' must be unique here!
Output_column_sel.append({'Catalog': 1, 'Column': 'TYPE',           'ID': 'id',     'OutputName': 'Flag_Laigle_TYPE'            }) # 'ID' must be unique in each catalog!
Output_column_sel.append({'Catalog': 2, 'Column': 'star',           'ID': 'ID',     'OutputName': 'Flag_Muzzin_star'            })
Output_column_sel.append({'Catalog': 2, 'Column': 'contamination',  'ID': 'ID',     'OutputName': 'Flag_Muzzin_contamination'   })
Output_column_sel.append({'Catalog': 3, 'Column': 'FLAG',           'ID': 'id',     'OutputName': 'Flag_Capak_FLAG'             })
Output_column_sel.append({'Catalog': 5, 'Column': 'col12',          'ID': 'ID',     'OutputName': 'Flag_Davidzon_col12'         })



## 
## def is_outlier
#def is_outlier(i):
#    iflag = \
#    numpy.logical_and(\
#    numpy.logical_and(\
#    numpy.logical_and(\
#    numpy.logical_and(\
#    numpy.logical_and(\
#    numpy.logical_or(globals()['Flag_Laigle_FLAG_PETER'][i]==0, globals()['Flag_Laigle_FLAG_PETER'][i]==-99),
#    numpy.logical_or(globals()['Flag_Laigle_TYPE'][i]==0, globals()['Flag_Laigle_TYPE'][i]==-99)),
#    numpy.logical_or(globals()['Flag_Muzzin_star'][i]==0, globals()['Flag_Muzzin_star'][i]==-99)),
#    numpy.logical_or(globals()['Flag_Muzzin_contamination'][i]==0, globals()['Flag_Muzzin_contamination'][i]==-99)),
#    numpy.logical_or(globals()['Flag_Capak_FLAG'][i]==0, globals()['Flag_Capak_FLAG'][i]==-99)),
#    numpy.logical_or(globals()['Flag_Davidzon_col12'][i]==0, globals()['Flag_Davidzon_col12'][i]==-99))
#    if iflag == True:
#        return 0
#    else:
#        return 1









# 
# Read the User-input 'Output_column_sel'
for var in Output_column_sel:
    print('Reading catalog %s column "%s" into variable "%s"'%(var['Catalog'], var['Column'], var['OutputName']))
    globals()[var['OutputName']] = (globals()['Cat_%d'%(var['Catalog'])]).getColumn(var['Column'])
    #print(var['OutputName'], globals()[var['OutputName']][0])
    globals()['ID_for_'+var['OutputName']] = globals()['ID_%d'%(var['Catalog'])] # (globals()['Cat_%d'%(var['Catalog'])]).getColumn(var['ID'])

sys.setrecursionlimit(10000)

for x in range(Cat_N):
    # -- try KDTree (seems must be 2D?)
    print('Making KDTree for Table %d IDs'%(x+1))
    globals()['KDTree_%d'%(x+1)] = KDTree(numpy.column_stack((globals()['ID_%d'%(x+1)], globals()['ID_%d'%(x+1)])))



# 
# Read the multi entry catalog which is the output of 
# do_make_master_catalog_step_1_multi_entries.py
Cat = Table.read('master_catalog_multi_entries.txt', format='ascii.commented_header')

for x in range(Cat_N):
    # Get master catalog aligned ID RA Dec Flag
    globals()['ID_%d'%(x+1)] = Cat['ID_%d'%(x+1)]
    globals()['RA_%d'%(x+1)] = Cat['RA_%d'%(x+1)]
    globals()['Dec_%d'%(x+1)] = Cat['Dec_%d'%(x+1)]
    globals()['Flag_%d'%(x+1)] = Cat['Flag_%d'%(x+1)]



# 
# Prepare output file
Output_File = 'master_catalog_single_entry.txt'
Output_fp = open(Output_File, 'w')


# 
# Prepare output file header
Output_header_fmt = ''
Output_header_var = []
Output_data_fmt = ''
Output_data_var = []
# 
Output_header_fmt = '# %13s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s\n'
# 
Output_data_fmt = '%15d %15.10f %15.10f %15d %15d %15d %15d %15d %15d %15d %15d %15d %15d\n' # ID RA Dec Flag Dupl ID_Origin, and 6 Flags
# 
Output_header_var.append('ID')
Output_header_var.append('RA')
Output_header_var.append('Dec')
Output_header_var.append('Flag')
Output_header_var.append('Dupl')
Output_header_var.append('ID_Origin')
# 
for var in Output_column_sel:
    Output_header_var.append(var['OutputName'])
# 
Output_header_var.append('Flag_Outlier') # last column
# 
Output_fp.write(Output_header_fmt%tuple(Output_header_var))



# 
# Loop each object in the catalog
for i in range(len(ID_1)):
    # 
    # <TODO> debug
    #if i < 718611:
    #    continue
    # 
    # Print progress
    if i == 0:
        sys.stdout.write('%0.0f%%'%(float(i+1)/(len(ID_1)/100.0)))
        sys.stdout.flush()
    elif ((float(i+1))%(len(ID_1)/100)) == 0:
        sys.stdout.write(' %0.0f%%'%(float(i+1)/(len(ID_1)/100.0)))
        sys.stdout.flush()
    if i == len(ID_1)-1:
        sys.stdout.write('\n')
        sys.stdout.flush()
    # 
    # initialize output array for object i
    Output_data_var = []
    # 
    # Get a unique ID in the master catalog
    Output_data_var.append(i+1)
    # 
    # Get the Duplication number
    Duplication = 0
    for x in range(Cat_N):
        if (globals()['Flag_%d'%(x+1)])[i] >= 0:
            # 
            if Duplication <= 0:
                Duplication = 1
            else:
                Duplication = Duplication + 1
    # 
    for x in range(Cat_N):
        if (globals()['Flag_%d'%(x+1)])[i] == 0:
            # Flag_N == 0 means the source is originally from this catalog
            Output_data_var.append( float((globals()['RA_%d'%(x+1)])[i]) )
            Output_data_var.append( float((globals()['Dec_%d'%(x+1)])[i]) )
            Output_data_var.append( int(x+1) ) # Flag indicating which catalog the source is originally from
            Output_data_var.append( int(Duplication) ) # the Duplication number
            Output_data_var.append( long((globals()['ID_%d'%(x+1)])[i]) ) # the original ID in the original catalog
            # break when found the original catalog entry
            break
    # 
    # Check Output_data_var
    if len(Output_data_var) != 6:
        print('Error! Failed to find Flag == 0 for Source ID %d in the multi entry master catalog!'%(i+1))
        sys.exit()
    # 
    # Get Output_column_sel
    debug_break = False
    row_is_outlier = 0
    for var in Output_column_sel:
        if (globals()['Flag_%d'%(var['Catalog'])])[i] >= 0: 
            # -- too slow
            #id_k = globals()['ID_for_'+var['OutputName']]
            id_j = (globals()['ID_%d'%(var['Catalog'])])[i]
            #row_indices = [ j for j, k in enumerate(id_k) if k == id_j ]
            #row_value = (globals()[var['OutputName']])[row_indices[0]]
            #row_value2 = (globals()['ID_for_'+var['OutputName']])[row_indices[0]]
            # 
            # -- try KDTree
            sep_dist, row_index = (globals()['KDTree_%d'%(var['Catalog'])]).query((id_j, id_j))
            if type(row_index) is list:
                row_index = row_index[0]
            row_value = (globals()[var['OutputName']])[row_index]
            row_value = int(row_value)
            # 
            # append to the output data array
            Output_data_var.append(row_value)
            # 
            # debug
            #if True:
            #    if i >= 5: debug_break = True
            #    print('Debug current ID %d ID_%d %d (original ID %d) %s[%d] = %d'%(
            #            (i+1), var['Catalog'], (globals()['ID_%d'%(var['Catalog'])])[i], (globals()['ID_for_'+var['OutputName']])[row_index], var['OutputName'], row_index, row_value))
            #if var['Catalog'] == 3:
            #    debug_break = True
            #    print('Debug current ID %d ID_%d %d (original ID %d) %s[%d] = %d'%(
            #            (i+1), var['Catalog'], (globals()['ID_%d'%(var['Catalog'])])[i], (globals()['ID_for_'+var['OutputName']])[row_index], var['OutputName'], row_index, row_value))
            # 
            # flag outlier
            if row_value != 0 and row_value != -99:
                row_is_outlier = 1
        else:
            Output_data_var.append(-99)
    # 
    # Flag
    Output_data_var.append(row_is_outlier)
    # 
    # Output 
    Output_fp.write(Output_data_fmt%tuple(Output_data_var))
    # 
    # 
    if debug_break:
        break


Output_fp.close()

print('Output to "%s"!'%(Output_File))

# 
# 
# 

print('')
print('Then please run the following command in terminal:')
print('    topcat -f ASCII "%s"'%(Output_File))
print('')
print('And add a new column named "Flag_Outlier" with the following expression: ')
print('    ($7==0 || $7==-99) && ($8==0 || $8==-99) && ($9==0 || $9==-99) && ($10==0 || $10==-99) && ($11==0 || $11==-99) && ($12==0 || $12==-99) ? 0 : 1')
print('')








