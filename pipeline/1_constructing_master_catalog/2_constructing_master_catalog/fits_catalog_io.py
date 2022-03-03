#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re
import numpy as np
from astropy.table import Table

class FITSCatalogIO():
    """FITS Catalog IO Class
    """
    def __init__(self, catalog_file):
        self.catalog_file = ''
        self.table = None
        self.colnames = []
        self.ID = None
        self.RA = None
        self.DEC = None
        self.REDSHIFT = None
        self.ZPHOT = None
        self.ZSPEC = None
        self.LOGMSTAR = None
        self.LOGMGAS = None
        self.LOGMH2 = None
        self.LOGMHI = None
        self.LOGSFR = None
        self.LOGSSFR = None
        self.LOGLUV = None
        self.LOGLIR = None
        self.E_REDSHIFT = None
        self.E_ZPHOT = None
        self.E_ZSPEC = None
        self.E_LOGMSTAR = None
        self.E_LOGMGAS = None
        self.E_LOGMH2 = None
        self.E_LOGMHI = None
        self.E_LOGSFR = None
        self.E_LOGSSFR = None
        self.E_LOGLUV = None
        self.E_LOGLIR = None
        self.REF_REDSHIFT = None
        self.REF_ZPHOT = None
        self.REF_ZSPEC = None
        self.REF_LOGMSTAR = None
        self.REF_LOGMGAS = None
        self.REF_LOGMH2 = None
        self.REF_LOGMHI = None
        self.REF_LOGSFR = None
        self.REF_LOGSSFR = None
        self.REF_LOGLUV = None
        self.REF_LOGLIR = None
        self.FIELD = None
        self.loadTable(catalog_file)
    
    def loadTable(self, catalog_file):
        self.catalog_file = catalog_file
        self.table = Table.read(self.catalog_file, format='fits')
        self.colnames = self.table.colnames
        self.ID = self.getColumn('ID', ['NUMBER'])
        self.RA = self.getColumn('RA', ['ALPHA_J2000'])
        self.DEC = self.getColumn('DEC', ['DELTA_J2000', 'DE'])
        self.REDSHIFT = self.getColumn('REDSHIFT', ['Z', 'ZPHOT', 'ZPHOTO', 'PHOTOZ', 'ZPDF'])
        self.ZPHOT = self.getColumn('ZPHOT', ['ZPHOTO', 'PHOTOZ', 'ZPDF'])
        self.ZSPEC = self.getColumn('ZSPEC', ['SPECZ'])
        self.REF_REDSHIFT = self.getColumn('REF_REDSHIFT', ['REF_Z', 'REF_ZPHOT', 'REF_ZPHOTO', 'REF_PHOTOZ', 'REF_ZPDF'])
        self.REF_ZPHOT = self.getColumn('REF_ZPHOT', ['REF_ZPHOTO', 'REF_PHOTOZ', 'REF_ZPDF'])
        self.REF_ZSPEC = self.getColumn('REF_ZSPEC', ['REF_SPECZ'])
        self.LOGMSTAR = self.getColumn('LOGMSTAR')
        self.E_LOGMSTAR = self.getColumn('E_LOGMSTAR')
        if self.LOGMSTAR is None:
            var = self.getColumn('MSTAR')
            if var is not None:
                self.LOGMSTAR = np.log10(var)
        self.LOGMGAS = self.getColumn('LOGMGAS')
        self.E_LOGMGAS = self.getColumn('E_LOGMGAS')
        self.REF_LOGMGAS = self.getColumn('REF_LOGMGAS')
        if self.LOGMGAS is None:
            var = self.getColumn('MGAS')
            if var is not None:
                self.LOGMGAS = np.log10(var)
        self.LOGMH2 = self.getColumn('LOGMH2', ['LOGMMOL', 'LOGMMOLGAS'])
        self.E_LOGMH2 = self.getColumn('E_LOGMH2', ['E_LOGMMOL', 'E_LOGMMOLGAS'])
        self.REF_LOGMH2 = self.getColumn('REF_LOGMH2', ['REF_LOGMMOL', 'REF_LOGMMOLGAS'])
        if self.LOGMH2 is None:
            var = self.getColumn('MH2', ['MMOL', 'MMOLGAS'])
            if var is not None:
                self.LOGMH2 = np.log10(var)
                var2 = self.getColumn('E_MH2', ['E_MMOL', 'E_MMOLGAS'])
                if var2 is not None:
                    self.E_LOGMH2 = var2/var
        self.LOGMHI = self.getColumn('LOGMHI')
        self.E_LOGMHI = self.getColumn('E_LOGMHI')
        self.REF_LOGMHI = self.getColumn('REF_LOGMHI')
        if self.LOGMHI is None:
            var = self.getColumn('MHI')
            if var is not None:
                self.LOGMHI = np.log10(var)
                var2 = self.getColumn('E_MHI')
                if var2 is not None:
                    self.E_LOGMHI = var2/var
        self.LOGSFR = self.getColumn('LOGSFR')
        self.E_LOGSFR = self.getColumn('E_LOGSFR')
        self.REF_LOGSFR = self.getColumn('REF_LOGSFR')
        if self.LOGSFR is None:
            var = self.getColumn('SFR')
            if var is not None:
                self.LOGSFR = np.log10(var)
                var2 = self.getColumn('E_SFR')
                if var2 is not None:
                    self.E_LOGSFR = var2/var
        self.LOGSSFR = self.getColumn('LOGSSFR')
        self.E_LOGSSFR = self.getColumn('E_LOGSSFR')
        self.REF_LOGSSFR = self.getColumn('REF_LOGSSFR')
        if self.LOGSSFR is None:
            var = self.getColumn('SSFR')
            if var is not None:
                self.LOGSSFR = np.log10(var)
                var2 = self.getColumn('E_SSFR')
                if var2 is not None:
                    self.E_LOGSSFR = var2/var
        self.LOGLUV = self.getColumn('LOGLUV')
        self.E_LOGLUV = self.getColumn('E_LOGLUV')
        self.REF_LOGLUV = self.getColumn('REF_LOGLUV')
        if self.LOGLUV is None:
            var = self.getColumn('LIR', ['LIR','L_IR'])
            if var is not None:
                self.LOGLUV = np.log10(var)
                var2 = self.getColumn('E_LIR', ['E_LIR','E_L_IR'])
                if var2 is not None:
                    self.E_LOGLUV = var2/var
        self.LOGLIR = self.getColumn('LOGLIR')
        self.E_LOGLIR = self.getColumn('E_LOGLIR')
        self.REF_LOGLIR = self.getColumn('REF_LOGLIR')
        if self.LOGLIR is None:
            var = self.getColumn('LIR', ['LIR','L_IR'])
            if var is not None:
                self.LOGLIR = np.log10(var)
                var2 = self.getColumn('E_LIR', ['E_LIR','E_L_IR'])
                if var2 is not None:
                    self.E_LOGLIR = var2/var
        self.FIELD = self.getColumn('FIELD')
        return
    
    def getColumn(self, column_name, alternative_column_names=None):
        if self.table is not None:
            matched_colname = ''
            for colname in self.colnames:
                if colname.upper().strip() == column_name.upper().strip():
                    matched_colname = colname
                    break
            # if no match, search alternative_column_names
            if matched_colname == '' and alternative_column_names is not None:
                if np.isscalar(alternative_column_names):
                    alternative_column_names = [alternative_column_names]
                for alt_column_name in alternative_column_names:
                    for colname in self.colnames:
                        if colname.upper().strip() == alt_column_name.upper().strip():
                            matched_colname = colname
                            break
                    if matched_colname != '':
                        break
            # if no match, remove any dash or slash characters then search by the column_name again
            if matched_colname == '' and re.match(r'^.*[^a-zA-Z0-9]+.*$', column_name) is not None:
                for colname in self.colnames:
                    if re.sub(r'[^a-zA-Z0-9]', r'', colname).upper().strip() == re.sub(r'[^a-zA-Z0-9]', r'', column_name).upper().strip():
                        matched_colname = colname
                        break
            # if no match, remove any dash or slash characters then search by the alternative_column_names again
            if matched_colname == '' and alternative_column_names is not None:
                if np.isscalar(alternative_column_names):
                    alternative_column_names = [alternative_column_names]
                for alt_column_name in alternative_column_names:
                    if re.match(r'^.*[^a-zA-Z0-9]+.*$', column_name):
                        for colname in self.colnames:
                            if re.sub(r'[^a-zA-Z0-9]', r'', colname).upper().strip() == re.sub(r'[^a-zA-Z0-9]', r'', alt_column_name).upper().strip():
                                matched_colname = colname
                                break
                    if matched_colname != '':
                        break
            # check if found matched colname
            if matched_colname != '':
                print('Reading column %s'%(matched_colname))
                return self.table[matched_colname]
            else:
                print('Warning! Column %r was not found in the table %r (%s)!'%(column_name, self.catalog_file, re.sub(r'[ \t\r\n]+', r' ', str(self.colnames))))
        return None
        




