#!/usr/bin/env python2.7
# 

import sys

from CrabFitsTable import CrabFitsTable

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

Cat_7 = CrabFitsTable('Catalog_Sanders_2007_SCosmos.fits') # IRAC == "scosmos_irac_200706.tbl"
ID_7 = Cat_7.getColumn('ID')
RA_7 = Cat_7.getColumn('RA')
Dec_7 = Cat_7.getColumn('DEC')
Sep_7 = 1.0 # arcsec

Cat_8 = CrabFitsTable('Catalog_Le_Floch_2009_COSMOS_24um.fits') # MIPS24 GO3 == "scosmos_mips_24_GO3_200810.tbl"
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
# Define output global variables
for x in range(Cat_N):
    globals()['Flag_%d'%(x+1)] = (globals()['RA_%d'%(x+1)]*0).astype(int)
    globals()['Output_ID_%d'%(x+1)] = -99
    globals()['Output_RA_%d'%(x+1)] = -99.0
    globals()['Output_Dec_%d'%(x+1)] = -99.0
    globals()['Output_Flag_%d'%(x+1)] = -99



# 
# Define output catalog file
Output_File = 'master_catalog_multi_entries.txt'
Output_fp = open(Output_File, 'w')



# 
# Define loop variables
Total_Obj = 0
Count_Obj = 0
Debug_level = 1



# 
# Loop each catalog to make KDTree
for x in range(Cat_N):
    print('Making KDTree for Table %d'%(x+1))
    globals()['RADec_%d'%(x+1)] = numpy.column_stack((globals()['RA_%d'%(x+1)]*numpy.cos(globals()['Dec_%d'%(x+1)]/180.0*numpy.pi), globals()['Dec_%d'%(x+1)]))
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
    #    closest_distances.append(numpy.sqrt((RADec_x[0]-RADec_y[0])**2 + (RADec_x[1]-RADec_y[1])**2) * 3600.0)
    #closest_pair_index = (numpy.argsort(closest_distances))[0]
    #print('The closest pair separation in Table %d is %.10f arcsec (pair object indexes %d and %d)'%(x+1,closest_distances[closest_pair_index],list(closest_pairs)[closest_pair_index][0],list(closest_pairs)[closest_pair_index][1]))


print("")


# 
# Prepare output file header
Output_header_fmt = ''
Output_header_var = []
Output_data_fmt = ''
Output_data_var = []
for x in range(Cat_N):
    # 
    if x == 0:
        Output_header_fmt = '# %13s %15s %15s %15s'
    else:
        Output_header_fmt = Output_header_fmt + ' %15s %15s %15s %15s'
    # 
    if x == Cat_N-1:
        Output_header_fmt = Output_header_fmt + '\n'
    # 
    Output_header_var.append('ID_%d'%(x+1))
    Output_header_var.append('RA_%d'%(x+1))
    Output_header_var.append('Dec_%d'%(x+1))
    Output_header_var.append('Flag_%d'%(x+1))
# 
Output_fp.write(Output_header_fmt%tuple(Output_header_var))


# 
# Loop each input catalog
for x in range(Cat_N):
    # 
    # Select catalog x
    print('Cross-matching objects in Table %d'%(x+1))
    ID_x = globals()['ID_%d'%(x+1)]
    RA_x = globals()['RA_%d'%(x+1)]
    Dec_x = globals()['Dec_%d'%(x+1)]
    Flag_x = globals()['Flag_%d'%(x+1)]
    RADec_x = globals()['RADec_%d'%(x+1)]
    KDTree_x = globals()['KDTree_%d'%(x+1)]
    # 
    # Loop each object in catalog x
    for j in range(len(ID_x)):
        # 
        # Count_Obj
        Count_Obj = Count_Obj + 1
        # 
        # Print progress
        if Debug_level >= 1:
            if j == 0:
                sys.stdout.write('%0.0f%%'%(float(Count_Obj)/(Total_Obj/100.0)))
                sys.stdout.flush()
            elif ((Count_Obj)%(Total_Obj/100)) == 0:
                sys.stdout.write(' %0.0f%%'%(float(Count_Obj)/(Total_Obj/100.0)))
                sys.stdout.flush()
            if j == len(ID_x)-1:
                sys.stdout.write('\n')
                sys.stdout.flush()
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
        for y in range(Cat_N):
            globals()['Output_ID_%d'%(y+1)] = -99
            globals()['Output_RA_%d'%(y+1)] = -99.0
            globals()['Output_Dec_%d'%(y+1)] = -99.0
            globals()['Output_Flag_%d'%(y+1)] = -99
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
            separation_limit = globals()['Sep_%d'%(y+1)] # arcsec
            distance_forward, index_forward = KDTree_y.query(RADec_x[j], k=10, distance_upper_bound=separation_limit/3600.0)
            distance_forward = distance_forward * 3600.0
            # 
            # skip if no valid cross-match
            if numpy.isnan(distance_forward[0]) == True or distance_forward[0] > 1.0:
                continue
            # 
            # found a cross-match, print the matched counterpart
            if Debug_level >= 2:
                print('%15s %s'%(' ', 'Found matched Table %d index %d to Table %d index %d'%(y+1,index_forward[0],x+1,j)))
            # 
            # reversed-cross-match y to x
            distance_backward, index_backward = KDTree_x.query(RADec_y[index_forward[0]], k=10, distance_upper_bound=separation_limit/3600.0)
            distance_backward = distance_backward * 3600.0
            # 
            # skip if no valid reversed-cross-match
            if numpy.isnan(distance_backward[0]) == True or distance_backward[0] > 1.0:
                continue
            # 
            # if the cross-match and reversed-cross-match agree
            if index_backward[0] == j:
                # 
                # mark as matched! store results!
                if True:
                    (globals()['Output_ID_%d'%(x+1)])  = (ID_x[index_backward[0]])
                    (globals()['Output_RA_%d'%(x+1)])  = (RA_x[index_backward[0]])
                    (globals()['Output_Dec_%d'%(x+1)]) = (Dec_x[index_backward[0]])
                    (globals()['Output_Flag_%d'%(x+1)]) = 0
                if y != x:
                    (globals()['Output_ID_%d'%(y+1)])  = (ID_y[index_forward[0]])
                    (globals()['Output_RA_%d'%(y+1)])  = (RA_y[index_forward[0]])
                    (globals()['Output_Dec_%d'%(y+1)]) = (Dec_y[index_forward[0]])
                    (globals()['Output_Flag_%d'%(y+1)]) = 1
                if True:
                    (globals()['Flag_%d'%(y+1)])[index_forward[0]] = 1
        # 
        # Prepare output data var list
        Output_data_fmt = ''
        Output_data_var = []
        for y in range(Cat_N):
            Output_data_var.append(globals()['Output_ID_%d'%(y+1)])
            Output_data_var.append(globals()['Output_RA_%d'%(y+1)])
            Output_data_var.append(globals()['Output_Dec_%d'%(y+1)])
            Output_data_var.append(globals()['Output_Flag_%d'%(y+1)])
            # 
            if globals()['Output_ID_%d'%(y+1)] > -99:
                if y == 0:
                    Output_data_fmt = '%15d %15.10f %15.10f %15d'
                else:
                    Output_data_fmt = Output_data_fmt + ' %15d %15.10f %15.10f %15d'
            else:
                if y == 0:
                    Output_data_fmt = '%15d %15.0f %15.0f %15d'
                else:
                    Output_data_fmt = Output_data_fmt + ' %15d %15.0f %15.0f %15d'
            # 
            if y == Cat_N-1:
                Output_data_fmt = Output_data_fmt + '\n'
        # 
        # Output 
        Output_fp.write(Output_data_fmt%tuple(Output_data_var))
        # 
        # 
        #pass
        #break
    #pass
    #break


Output_fp.close()

print('Output to "%s"!'%(Output_File))





