#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re, shutil, gzip, glob
import numpy as np
from astropy.table import Table, Column, MaskedColumn
from astropy.table import join as astropy_table_join
import astroquery
from astroquery.utils.tap.core import TapPlus
import configparser
class CaseConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr


class CDSCatalogIO():
    """CDS Catalog IO Class
    """
    def __init__(self, catalog_meta_file, catalog_cache_pool=None):
        self.catalog_meta_file = ''
        self.catalog_cache_dir = ''
        self.iniparser = None
        self.table = None
        self.colnames = []
        self.TAP_server = None
        self.TAP_server_url = "http://tapvizier.u-strasbg.fr/TAPVizieR/tap"
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
        self.loadTable(catalog_meta_file, catalog_cache_pool)
    
    def buildQueryCommand(self, table, columns, cache_command):
        query_command = "SELECT "
        for key in columns.keys():
            query_command += "\"%s\".%s , "%(table, columns[key])
        query_command = query_command.rstrip(", ")
        query_command += " \n"
        query_command += "FROM \"%s\""%(table)
        print('query_command:\n%s'%(query_command))
        with open(cache_command, 'w') as fp:
            fp.write(query_command+"\n")
        return query_command
    
    def runQueryJob(self, query_command, cache_table, cache_jobid, cache_colnames, overwrite=False):
        # try to load cache
        can_load_cache = False
        if os.path.isfile(cache_table) and not overwrite: 
            job = None
            r = Table.read(cache_table, format='votable')
            can_load_cache = True
        # if we can not load cache or overwrite is set, then try to resume a job or launch a new job
        if not can_load_cache:
            # prepare to connect to TAP server
            if self.TAP_server is None:
                self.TAP_server = TapPlus(url=self.TAP_server_url)
            # try to resume an async job
            can_resume_job = False
            if os.path.isfile(cache_jobid) and not overwrite:
                with open(cache_jobid, 'r') as fp:
                    jobid = int(fp.readline())
                try:
                    job = self.TAP_server.load_async_job(jobid)
                    if job is not None:
                        can_resume_job = True
                except:
                    can_resume_job = False
            # if no async job to resume, then we launch a new async query job
            if not can_resume_job:
                job = self.TAP_server.launch_job_async(query_command, dump_to_file=True, output_file=cache_table, output_format='votable', verbose=True)
                with open(cache_jobid, 'w') as fp:
                    fp.write('%s\n'%(str(job.jobid)))
            # print job
            print('job:\n', job)
            # get result table
            r = job.get_results()
            # save column names
            with open(cache_colnames, 'w') as fp:
                for col in r.colnames:
                    fp.write(col+'\n')
        # return job and result table
        return job, r
    
    def queryCDS(self, overwrite=False):
        """Query CDS server with astroquery TAP
        """
        iniparser = self.iniparser
        catalog_cache_dir = self.catalog_cache_dir
        catalog_meta_file = self.catalog_meta_file
        # for TAP API, see -- https://astroquery.readthedocs.io/en/latest/utils/tap.html
        if (not os.path.isfile(catalog_cache_dir+os.sep+'table.fits') and not os.path.isfile(catalog_cache_dir+os.sep+'table.fits.gz')) or overwrite:
            check_ok = True
            if 'CDS' not in iniparser.sections():
                print('Error! The input catalog meta file must be an INI-format file and contain a [CDS] section!')
                check_ok = False
            for key in ['TABLE']:
                if key not in iniparser['CDS']:
                    print('Error! The input catalog meta file should contain key %s in the [CDS] section!'%(key))
                    check_ok = False
            if 'COLUMNS' not in iniparser.sections():
                print('Error! The input catalog meta file must be an INI-format file and contain a [COLUMNS] section!')
                check_ok = False
            for key in ['RA', 'DEC']:
                if key not in iniparser['COLUMNS']:
                    print('Error! The input catalog meta file should contain key %s in the [COLUMNS] section!'%(key))
                    check_ok = False
            if not check_ok:
                print('Error! The input catalog meta file %r seem to be invalid!'%(catalog_meta_file))
                raise Exception('Error! The input catalog meta file %r seem to be invalid!'%(catalog_meta_file))
            # 
            if 'QUERY_COMMAND' in iniparser['CDS']:
                query_command = iniparser['CDS']['QUERY_COMMAND']
                with open(catalog_cache_dir+os.sep+'query_command.txt', 'w') as fp:
                    fp.write(query_command+'\n')
            else:
                query_command = self.buildQueryCommand(table=iniparser['CDS']['TABLE'], columns=iniparser['COLUMNS'], 
                                                       cache_command=catalog_cache_dir+os.sep+'query_command.txt')
            # 
            job, r = self.runQueryJob(query_command, cache_table=catalog_cache_dir+os.sep+'cache.votable', 
                                      cache_jobid=catalog_cache_dir+os.sep+'query_jobid.txt', 
                                      cache_colnames=catalog_cache_dir+os.sep+'query_colnames.txt', 
                                      overwrite=overwrite)
            # more tables to concatenate
            #if 'TABLES_TO_CONCAT' in iniparser['CDS']:
            #    tables_to_concat = eval(iniparser['CDS']['TABLES_TO_CONCAT'])
            #    if np.isscalar(tables_to_concat):
            #        tables_to_concat = [tables_to_concat]
            #    print('got tables to concatenate: %s'%(re.sub(r'[ \t\r\n]+', r' ', str(tables_to_concat))))
            #    for iconcat, table_to_concat in enumerate(tables_to_concat):
            #        query_cmd2 = self.buildQueryCommand(table=table_to_concat, columns=iniparser['COLUMNS'], cache_command=catalog_cache_dir+os.sep+'query_command_%d.txt'%(iconcat+2))
            #        job2, r2 = self.runQueryJob(query_cmd2, cache_table=catalog_cache_dir+os.sep+'cache_%d.votable'%(iconcat+2), 
            #                                    cache_jobid=catalog_cache_dir+os.sep+'jobid_%d.txt'%(iconcat+2), 
            #                                    cache_colnames=catalog_cache_dir+os.sep+'query_colnames.txt', 
            #                                    overwrite=overwrite)
            #        # join columns
            #        key_to_join = None
            #        if 'TABLES_TO_CONCAT_BY_COLUMN' in iniparser['CDS']:
            #            key_to_join = iniparser['CDS']['TABLES_TO_CONCAT_BY_COLUMN']
            #            print('joining tables by key: %s'%(key_to_join))
            #        r = astropy_table_join(r, r2, keys=key_to_join, join_type='left', table_names=['','%d'%(iconcat+2)])
            # rename columns
            print('renaming columns')
            for key in iniparser['COLUMNS'].keys():
                if iniparser['COLUMNS'][key] in r.colnames:
                    print('renaming column %s to %s'%(iniparser['COLUMNS'][key], key))
                    r.rename_column(iniparser['COLUMNS'][key], key)
            # fix column object type
            for col in r.colnames:
                print('r[%r].type: %s, r[%r].dtype: %s'%(col, type(r[col]), col, str(r[col].dtype)))
                if r[col].dtype == object:
                    r[col] = r[col].astype('|S')
            # save to disk
            if os.path.isfile(catalog_cache_dir+os.sep+'table.fits'):
                shutil.move(catalog_cache_dir+os.sep+'table.fits', catalog_cache_dir+os.sep+'table.fits.backup')
            r.write(catalog_cache_dir+os.sep+'table.fits', format='fits')
            print('Output to "%s"'%(catalog_cache_dir+os.sep+'table.fits'))
            # gzip
            if os.path.isfile(catalog_cache_dir+os.sep+'table.fits.gz'):
                shutil.move(catalog_cache_dir+os.sep+'table.fits.gz', catalog_cache_dir+os.sep+'table.fits.gz.backup')
            with open(catalog_cache_dir+os.sep+'table.fits', 'rb') as f_in:
                with gzip.open(catalog_cache_dir+os.sep+'table.fits.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print('Output to "%s"'%(catalog_cache_dir+os.sep+'table.fits.gz'))
            # remove dump files and the ungzipped file, so that we only keep the final gzipped file table.fits.gz
            if os.path.isfile(catalog_cache_dir+os.sep+'table.fits.gz'):
                if os.path.isfile(catalog_cache_dir+os.sep+'table.fits'):
                    os.remove(catalog_cache_dir+os.sep+'table.fits')
                # and remove dump file
                list_of_cache_files = glob.glob(catalog_cache_dir+os.sep+'cache*.votable')
                if len(list_of_cache_files) > 0:
                    for cache_file in list_of_cache_files:
                        os.remove(cache_file)
        else:
            print('Reading cache "%s" (to requery CDS, set overwrite to True then rerun queryCDS)'%(catalog_cache_dir+os.sep+'table.fits'))
            if os.path.isfile(catalog_cache_dir+os.sep+'table.fits.gz'):
                r = Table.read(catalog_cache_dir+os.sep+'table.fits.gz', format='fits')
            else:
                r = Table.read(catalog_cache_dir+os.sep+'table.fits', format='fits')
        return r
    
    def loadTable(self, catalog_meta_file, catalog_cache_pool=None, overwrite=False):
        # first read the meta file
        # it must contain certain sections and certain keys
        self.catalog_meta_file = catalog_meta_file
        if catalog_cache_pool is None:
            catalog_cache_pool = os.path.dirname(os.path.abspath(catalog_meta_file))
        self.catalog_cache_dir = catalog_cache_pool + os.sep + re.sub(r'(_meta_info|)\.ini$', r'', os.path.basename(catalog_meta_file))
        self.iniparser = CaseConfigParser()
        self.iniparser.read(self.catalog_meta_file)
        if not os.path.isdir(self.catalog_cache_dir):
            os.makedirs(self.catalog_cache_dir)
        self.table = self.queryCDS(overwrite=overwrite)
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
                print('Warning! Column %r was not found in the table %r (%s)!'%(column_name, self.catalog_meta_file, re.sub(r'[ \t\r\n]+', r' ', str(self.colnames))))
        return None
    
    def getPhotometryByID(self, ID):
        if self.table is not None and self.iniparser is not None:
            if 'PHOTOMETRY' in self.iniparser.sections():
                check_ok = True
                for key in ['BANDS', 'FILETERS', 'WAVELENGTHS', 'FLUX_CONV', 'FLUX_PREFIX', 'FLUXERR_PREFIX']:
                    if key not in self.iniparser['PHOTOMETRY']:
                        print('Error! The input catalog meta file should contain key %s in the [PHOTOMETRY] section!'%(key))
                        check_ok = False
                if not check_ok:
                    print('Error! The input catalog meta file %r seem to be invalid!'%(self.catalog_meta_file))
                    raise Exception('Error! The input catalog meta file %r seem to be invalid!'%(self.catalog_meta_file))
                # 
                pass
    
    def getPhotometryByRADEC(self, RA, DEC):
        if self.table is not None and self.iniparser is not None:
            if 'PHOTOMETRY' in self.iniparser.sections():
                check_ok = True
                for key in ['BANDS', 'FILETERS', 'WAVELENGTHS', 'FLUX_CONV', 'FLUX_PREFIX', 'FLUXERR_PREFIX']:
                    if key not in self.iniparser['PHOTOMETRY']:
                        print('Error! The input catalog meta file should contain key %s in the [PHOTOMETRY] section!'%(key))
                        check_ok = False
                if not check_ok:
                    print('Error! The input catalog meta file %r seem to be invalid!'%(self.catalog_meta_file))
                    raise Exception('Error! The input catalog meta file %r seem to be invalid!'%(self.catalog_meta_file))
                # 
                pass
    




