#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re, copy, json, shutil, gzip, glob, fnmatch
import numpy as np
from collections import OrderedDict
from six import string_types
import astropy.units as u
from astropy.table import Table, Column, MaskedColumn
from astropy.table import join as astropy_table_join
from astropy.coordinates import SkyCoord, FK5
import synphot
from operator import attrgetter
import shapely
from shapely.geometry import Polygon, Point


class HighzDeepFieldDB(object):
    """High-redshift deep field database class."""
    def __init__(self, arg):
        super(HighzDeepFieldDB, self).__init__()
        self.arg = arg
        self.footprints = None
        self.deepfields = None
        # 
        footprints = {}
        # below are based on Spitzer
        footprints['COSMOS'] = 'Polygon 150.8561226705 1.4569151527 149.3610944277 1.4569151527 149.3610944277 2.9523607547 150.8561226705 2.9523607547'
        #footprints['EGS'] = 'Polygon 216.1905996434 53.5597281756 213.4145347440 53.5597281756 213.4145347440 52.0082445543 216.1905996434 52.0082445543'
        #footprints['GOODSN'] = 'Polygon 189.6448516062 62.0377800049 188.8068286619 62.0377800049 188.8068286619 62.4381010049 189.6448516062 62.4381010049'
        #footprints['GOODSS'] = 'Polygon 53.3324732328 -28.0050957288 52.9138001010 -28.0050957288 52.9138001010 -27.6047666961 53.3324732328 -27.6047666961'
        footprints['HUDF'] = 'Polygon 53.1916703549 -27.8114718946 53.1279585479 -27.8114718946 53.1279585479 -27.7567055806 53.1916703549 -27.7567055806'
        footprints['UDS'] = 'Polygon 35.2189407247 -5.9906420241 33.8017060409 -5.9906420241 33.8017060409 -4.2455945110 35.2189407247 -4.2455945110'
        # below are based on Herschel
        #footprints['COSMOS'] = ''
        footprints['GOODSN'] = 'Polygon 189.6588340448 62.0462372644 188.7914550210 62.0462372644 188.7914550210 62.4302203622 189.6588340448 62.4302203622'
        footprints['GOODSS'] = 'Polygon 53.3497211401 -28.0385678514 52.8960043653 -28.0385678514 52.8960043653 -27.5705728906 53.3497211401 -27.5705728906'
        footprints['ECDFS'] = 'Polygon 53.6525403701 -28.2709155050 52.5958883154 -28.2709155050 52.5958883154 -27.3363064305 53.6525403701 -27.3363064305'
        footprints['EGS'] = 'Polygon 216.1221202078 52.0191666791 213.4725685643 52.0191666791 213.4725685643 53.6192893608 216.1221202078 53.6192893608'
        footprints['LockmanHole'] = 'Polygon 163.6719018398 57.1987216948 162.6772942131 57.1987216948 162.6772942131 57.7600245177 163.6719018398 57.7600245177'
        footprints['A1689'] = 'Polygon 197.9562758359 -1.4213867709 197.7888970261 -1.4213867709 197.7888970261 -1.2540537123 197.9562758359 -1.2540537123'
        footprints['A1835'] = 'Polygon 210.3417654773 2.7955525662 210.1742207113 2.7955525662 210.1742207113 2.9628855528 210.3417654773 2.9628855528'
        footprints['A2218'] = 'Polygon 249.1718572597 66.1206998364 248.7571170236 66.1206998364 248.7571170236 66.2880297471 249.1718572597 66.2880297471'
        footprints['A2219'] = 'Polygon 250.2046786648 46.6285425771 249.9606307107 46.6285425771 249.9606307107 46.7958743785 250.2046786648 46.7958743785'
        footprints['A2390'] = 'Polygon 328.4915974284 17.6122024873 328.3159529621 17.6122024873 328.3159529621 17.7795351945 328.4915974284 17.7795351945'
        footprints['A370'] = 'Polygon 40.0542012557 -1.6619425162 39.8868045626 -1.6619425162 39.8868045626 -1.4946094536 40.0542012557 -1.4946094536'
        footprints['CL0024'] = 'Polygon 6.7720268171 17.0457970764 6.5271209992 17.0457970764 6.5271209992 17.2797957963 6.7720268171 17.2797957963'
        footprints['MS0451'] = 'Polygon 73.6334553091 -3.0999999925 73.4658899957 -3.0999999925 73.4658899957 -2.9326669057 73.6334553091 -2.9326669057'
        footprints['MS1054'] = 'Polygon 164.3344325820 -3.7576091125 164.1667641929 -3.7576091125 164.1667641929 -3.4902764887 164.3344325820 -3.4902764887'
        footprints['MS1358'] = 'Polygon 210.1562801074 62.4265506742 209.7937582602 62.4265506742 209.7937582602 62.5938811803 210.1562801074 62.5938811803'
        footprints['RXJ0152'] = 'Polygon 28.3083020366 -14.0957941364 28.0328307885 -14.0957941364 28.0328307885 -13.8284616739 28.3083020366 -13.8284616739'
        footprints['RXJ13475'] = 'Polygon 206.9622263916 -11.8358205747 206.7913105934 -11.8358205747 206.7913105934 -11.6684873439 206.9622263916 -11.6684873439'
        # below are from rough estimates
        footprints['DEEP'] = 'Circle 171.2557083333 -21.6680000000 1.0'
        # 
        self.set_footprints(footprints)
    
    def set_footprints(self, footprints):
        self.footprints = footprints
        self.deepfields = {}
        if type(footprints) is not dict:
            raise Exception('Error! Please input a dictionary as the footprints!')
        for key in footprints:
            val = footprints[key].lower()
            #if val.find('union'):
            #    val_list = val.split('union')
            if val.startswith('polygon '):
                this_coord_list = re.sub(r'^polygon (.*)$', r'\1', val).split()
                this_coord_list = [(float(x),float(y)) for x,y in list(zip(this_coord_list[0::1], this_coord_list[1::1]))]
                if this_coord_list[0] != this_coord_list[-1]:
                    this_coord_list.append(this_coord_list[0]) # make it closed
                this_shape = Polygon(this_coord_list)
            elif val.startswith('circle '):
                this_coord_list = re.sub(r'^circle (.*)$', r'\1', val).split()
                this_coord_list = [(float(x),float(y),float(z)) for x,y,z in list(zip(this_coord_list[0::1], this_coord_list[1::1], this_coord_list[2::1]))]
                this_shape = Point(this_coord_list[0], this_coord_list[1]).buffer(this_coord_list[2])
            elif val.startswith('rect '):
                # rect x1 y1 x2 y2
                this_coord_list = re.sub(r'^rect (.*)$', r'\1', val).split()
                this_coord_list = [(float(x1),float(y1),float(x2),float(y2)) for x1,y1,x2,y2 in list(zip(this_coord_list[0::1], this_coord_list[1::1], this_coord_list[2::1], this_coord_list[3::1]))]
                this_shape = Polygon([(this_coord_list[0], this_coord_list[1]), 
                                      (this_coord_list[2], this_coord_list[1]), 
                                      (this_coord_list[2], this_coord_list[3]), 
                                      (this_coord_list[0], this_coord_list[3]),
                                      (this_coord_list[0], this_coord_list[1])])
            self.deepfields[key]['shape'] = this_shape
    
    def get_field_by_ra_dec(self, ra, dec):
        
