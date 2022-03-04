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
#import synphot
#from synphot import SourceSpectrum 
# synphot is used to convert Vega mag to flux
# f_Ks = synphot.units.convert_flux(2.15e-6*u.m, tb['Ks']*synphot.units.VEGAMAG, synphot.units.FNU, vegaspec=SourceSpectrum.from_vega()) # https://sites.astro.caltech.edu/palomar/observer/200inchResources/P200filters.html, WIRC
# f_Ks = f_Ks.to(u.Jy)
from operator import attrgetter
import astroquery
from astroquery.utils.tap.core import TapPlus
import configparser
class CaseConfigParser(configparser.ConfigParser):
    # This is used to keep the cases of key names in the configparser file
    def optionxform(self, optionstr):
        return optionstr
class MultiOrderedDict(OrderedDict):
    # This is used to allow for duplicated keys in the configparser file
    def __setitem__(self, key, value):
        #if isinstance(value, list) and key in self:
        #    #if not isinstance(self[key], list): 
        #    #    self[key] = [self[key]]
        #    #print('MultiOrderedDict setitem key %r, value = %s'%(key, value))
        #    #print('MultiOrderedDict setitem key %r, self[key] = %s'%(key, self[key]))
        #    #print('MultiOrderedDict setitem key %r, type(value) = %s, type(self[key]) = %s'%(key, type(value), type(self[key])))
        #    self[key].extend(value)
        #else:
        #    super(MultiOrderedDict, self).__setitem__(key, value)
        if isinstance(value, list) and key in self:
            idup = 1
            while '__%d__ %s'%(idup, key) in self:
                idup += 1
            keynodup = '__%d__ %s'%(idup, key)
            super(MultiOrderedDict, self).__setitem__(keynodup, value)
        else:
            super(MultiOrderedDict, self).__setitem__(key, value)
    def keys(self):
        return super(MultiOrderedDict, self).keys()
    #def keys(self):
    #    list_keys = super(MultiOrderedDict, self).keys()
    #    list_keysnodup = []
    #    for key in list_keys:
    #        if re.match(r'^__([0-9]+)__ (.*)$', key):
    #            continue
    #        list_keysnodup.append(key)
    #    return list_keysnodup
    #def items(self):
    #    # retrieve (key, value) pairs in the order they were initialized using _keys
    #    list_items = list_keys = super(MultiOrderedDict, self).items()
    #    list_itemsnodup = []
    #    #for k in self._keys
    #    # self.__dict__[key]
    #    for key, value in list_items:
    #        if re.match(r'^__([0-9]+)__ (.*)$', key):
    #            continue
    #        list_itemsnodup.append((key, value))
    #    return list_itemsnodup
    #@staticmethod
    #def getlist(value):
    #    return value.split(os.linesep)

class HighzGalaxyCatalogIO(object):
    """High-z Galaxy Catalog IO Class
    """
    def __init__(self, catalog_meta_file, catalog_cache_pool=None, verbose=True, overwrite=False):
        self.catalog_meta_file = ''
        self.catalog_cache_dir = ''
        self.iniparser = None
        self.access = ''
        self.file = ''
        self.ref = ''
        self.table = None # the astropy.table.Table object
        self.colnames = []
        self.TAP_server = None
        self.TAP_server_url = ""
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
        self.QUALITY_ZSPEC = None
        self.REF_LOGMSTAR = None
        self.REF_LOGMGAS = None
        self.REF_LOGMH2 = None
        self.REF_LOGMHI = None
        self.REF_LOGSFR = None
        self.REF_LOGSSFR = None
        self.REF_LOGLUV = None
        self.REF_LOGLIR = None
        self.FIELD = None
        self.loadTable(catalog_meta_file, catalog_cache_pool, verbose=verbose, overwrite=overwrite)
    
    def __len__(self):
        return len(self.ID)
    
    def buildQueryCommand(self, table, columns, cache_command):
        query_command = "SELECT "
        for key in columns.keys():
            colnamestr = columns[key]
            if colnamestr.find('.') >= 0 or colnamestr.find('[') >= 0 or colnamestr.find('-') >= 0 or colnamestr.find("'") >= 0:
                colnamestr = '"{}"'.format(colnamestr)
            query_command += "\"%s\".%s , "%(table, colnamestr)
        query_command = query_command.rstrip(", ")
        query_command += " \n"
        query_command += "FROM \"%s\""%(table)
        print('query_command:\n%s'%(query_command))
        with open(cache_command, 'w') as fp:
            fp.write(query_command+"\n")
        return query_command
    
    def runQueryJob(self, query_command, server_url, cache_table, cache_jobid, cache_colnames, overwrite=False):
        # try to load cache
        can_load_cache = False
        if os.path.isfile(cache_table) and not overwrite: 
            job = None
            print('reading cached votable %s'%(cache_table))
            tb = Table.read(cache_table, format='votable')
            can_load_cache = True
        # if we can not load cache or overwrite is set, then try to resume a job or launch a new job
        if not can_load_cache:
            # prepare to connect to TAP server
            do_new_connection = True
            if self.TAP_server is not None and self.TAP_server_url == server_url:
                do_new_connection = False
            if do_new_connection:
                self.TAP_server = TapPlus(url=server_url)
                self.TAP_server_url = server_url
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
            tb = job.get_results()
            # save column names
            with open(cache_colnames, 'w') as fp:
                for col in tb.colnames:
                    fp.write(col+'\n')
        # return job and result table
        return job, tb
    
    def saveTableToDisk(self, table, outfile, outfmt='fits', compression=True, verbose=True, overwrite=True, backup=True, remove_dump_files=None):
        """Save a table to disk in FITS format, do compression if needed.
        """
        # 
        # check self.iniparser
        if self.iniparser is None:
            return
        # 
        # check outfile compressed file name
        if outfile.endswith('.gz'):
            compression = True
            outfile = re.sub(r'\.gz$', r'', outfile)
        # 
        # check outfile
        if compression:
            if os.path.isfile(outfile+'.gz') and not overwrite:
                print('Found existing outfile "%s" and overwrite=False, skipping.'%(outfile+'.gz'))
                return
        else:
            if os.path.isfile(outfile) and not overwrite:
                print('Found existing outfile "%s" and overwrite=False, skipping.'%(outfile))
                return
        # 
        # copy table
        tb = table
        # 
        # fix column object type
        print('fixing column object type')
        for col in tb.colnames:
            if verbose:
                print('tb[%r].type: %s, tb[%r].dtype: %s'%(col, type(tb[col]), col, str(tb[col].dtype)))
            if tb[col].dtype == object:
                tb[col] = tb[col].astype('|S')
        # 
        # check outdir
        if outfile.find(os.sep) >= 0:
            if not os.path.isdir(os.path.dirname(outfile)):
                os.makedirs(os.path.dirname(outfile))
        # 
        # backup file
        if os.path.isfile(outfile): 
            if backup:
                shutil.move(outfile, outfile+'.backup')
            else:
                os.remove(outfile)
        # 
        # save to disk
        tb.write(outfile, format=outfmt)
        if verbose:
            print('Output to "%s"'%(outfile))
        # 
        # check if save_ok and do compression or not
        save_ok = os.path.isfile(outfile)
        if compression:
            # 
            # backup file
            if os.path.isfile(outfile+'.gz'): 
                if backup:
                    shutil.move(outfile+'.gz', outfile+'.gz.backup')
                else:
                    os.remove(outfile+'.gz')
            # 
            # compress file with gzip
            with open(outfile, 'rb') as f_in:
                with gzip.open(outfile+'.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            if verbose:
                print('Output to "%s"'%(outfile+'.gz'))
            # 
            # remove the ungzipped file
            if os.path.isfile(outfile+'.gz') and os.path.isfile(outfile):
                os.remove(outfile)
                save_ok = True
        # 
        # remove dump files if save to disk succeedded
        if save_ok and remove_dump_files is not None:
            if np.isscalar(remove_dump_files):
                remove_dump_files = [remove_dump_files]
            for dump_file in remove_dump_files:
                if dump_file.find('*') >= 0:
                    list_of_cache_files = glob.glob(dump_file)
                    if len(list_of_cache_files) > 0:
                        for cache_file in list_of_cache_files:
                            os.remove(cache_file)
                else:
                    os.remove(dump_file)
        # 
        # return
        return
    
    def validateCatalogMetaInfo(self, required_sections_keys=None, exit_on_error=True):
        """Validate the catalog meta info. 
        
        The input is self.iniparser, a configparser.ConfigParser object for the INI-format catalog meta file. 
        
        It should contain a [TABLE] section, a [COLUMNS] section, and optionally [ASTROMETRY] and [PHOTOMETRY] sections.
        
        The [TABLE] section of the meta file should contain 'ACCESS', 'TAP' or 'FILE', and 'TABLE' keys. 
        The 'ACCESS' key can be either 'TAP' or 'FILE'. If 'ACCESS' is 'TAP', then the key 'TAP' should be defined to the server URL. 
        Or if 'ACCESS' is 'FILE', then the file path of the table should be defined in the 'FILE' key. 
        The 'Table' key should be the table name used for querying if the access method needs it. 
        
        This function is called at the construction of this class, so users do not need to call it by their own. 
        
        """
        if self.iniparser is None:
            return False
        # 
        mandatory_sections_keys = {'TABLE':['ACCESS','TABLE','REF'], 'COLUMNS':['ID','RA','DEC']}
        # 
        acceptable_key_values = {'ACCESS':['TAP','FILE']}
        # 
        if required_sections_keys is None:
            checking_sections_keys = mandatory_sections_keys
        else:
            checking_sections_keys = copy.copy(mandatory_sections_keys)
            checking_sections_keys.update(required_sections_keys)
        # 
        check_ok = True
        for section_name in checking_sections_keys:
            if section_name not in self.iniparser.sections():
                print('Error! The input catalog meta file must be an INI-format file and contain a [%s] section!'%(section_name))
                check_ok = False
            else:
                for key_name in checking_sections_keys[section_name]:
                    if key_name not in self.iniparser[section_name]:
                        print('Error! The input catalog meta file should contain key %s in the [%s] section!'%(key_name, section_name))
                        check_ok = False
                    else:
                        if key_name in acceptable_key_values:
                            key_value = self.iniparser[section_name][key_name]
                            if key_value not in acceptable_key_values[key_name]:
                                print('Error! The input catalog meta file has an invalid key %s in the [%s] section! Value: %r. Acceptable value: %s.'%(\
                                    key_name, section_name, key_value, ', '.join('"{0}"'.format(t) for t in acceptable_key_values[key_name])))
                                check_ok = False
        if not check_ok and exit_on_error:
            print('Error! The input catalog meta file %r seems to be invalid!'%(self.catalog_meta_file))
            raise Exception('Error! The input catalog meta file %r seems to be invalid!'%(self.catalog_meta_file))
        # 
        return check_ok
    
    def renameColumns(self, table, column_key_values, verbose=True):
        """Rename colume names of the input table according to the column_key_values, return the result table.
        
        The column_key_values should be a dictionary, where key is the new column name and value is the old column name.
        """
        tb = table
        if verbose:
            print('renaming columns')
        key_list = list(column_key_values.keys())
        for ikey, key in enumerate(key_list):
            old_colname = column_key_values[key]
            if old_colname not in tb.colnames:
                if old_colname.find('.') >= 0:
                    old_colname = old_colname.replace('.', '_') # it seems astroquery astropy.table will convert '.' in colname as '_'
            if old_colname not in tb.colnames:
                if old_colname.find('[') >= 0:
                    old_colname = old_colname.replace('[', '_') # it seems astroquery astropy.table will convert '.' in colname as '_'
                if old_colname.find(']') >= 0:
                    old_colname = old_colname.replace(']', '_') # it seems astroquery astropy.table will convert '.' in colname as '_'
            if old_colname not in tb.colnames:
                if old_colname.find("'") >= 0:
                    old_colname = old_colname.replace("'", '_') # it seems astroquery astropy.table will convert '.' in colname as '_'
            if old_colname not in tb.colnames:
                if '_'+old_colname in tb.colnames:
                    old_colname = '_'+old_colname # it seems astroquery astropy.table will convert '.' in colname as '_'
            if old_colname in tb.colnames:
                #print('checkin ' + old_colname + ' in ' + str(key_list[ikey+1:]))
                #print('checkin ' + old_colname + ' in ' + str([column_key_values[k] for k in key_list[ikey+1:]]))
                if old_colname in key_list[ikey+1:] or old_colname in [column_key_values[k] for k in key_list[ikey+1:]]:
                    if verbose:
                        print('acopying column %r as %r'%(old_colname, key))
                    if key in tb.colnames:
                        tb[key] = tb[old_colname]
                    else:
                        old_colindex = tb.colnames.index(old_colname)
                        tb.add_column(tb[old_colname], name=key, index=old_colindex) # if old_colname is used in later column_key_values items, then do not rename but copy the column
                else:
                    if verbose:
                        print('renaming column %r to %r'%(old_colname, key))
                    tb.rename_column(old_colname, key)
        return tb
    
    def applyColumnUnits(self, table, column_unit_dict, verbose=True):
        """Apply units of the columns in the input table according to the column_unit_dict, return the result table.
        
        The column_unit_dict should be a dictionary, where key is the column name and value is the units string.
        """
        tb = table
        if verbose:
            print('setting column units')
        for col in tb.colnames:
            if col in column_unit_dict:
                this_column_unit = column_unit_dict[col] # the unit can be an unit string or an expression, e.g., "0.3631 * u.uJy"
                if isinstance(this_column_unit, string_types):
                    if this_column_unit.find('u.') >= 0:
                        this_column_unit = eval(this_column_unit)
                    elif this_column_unit.strip() == '':
                        this_column_unit = None
                    else:
                        this_column_unit = u.Unit(this_column_unit)
                if this_column_unit is not None:
                    if tb[col].unit != this_column_unit:
                        if verbose:
                            print('setting column %r unit %r to %r'%(col, tb[col].unit, this_column_unit))
                        tb[col].unit = this_column_unit
                # for flux columns, we convert them all to u.Jy
                if col.startswith('FLUX'):
                    if verbose:
                        print('converting column %r unit %r to %r'%(col, tb[col].unit, u.Jy))
                    #tb[col] = tb[col].to(u.Jy)
                    print('tb[%r].unit = %r'%(col, tb[col].unit.__str__()))
                    print('type(tb[%r].data) = %r'%(col, type(tb[col].data)))
                    if col.startswith('FLUXERR') and tb[col].unit.__str__().startswith('mag'):
                        col_flux = re.sub(r'^FLUXERR', r'FLUX', col)
                        if tb[col_flux].unit != u.Jy:
                            tb[col_flux] = tb[col_flux].to(u.Jy)
                        tb[col] = tb[col_flux] * tb[col].data / 1.086 # convert flux error from magnitude error
                        tb[col].unit = tb[col_flux].unit
                        print('tb[%r].unit = %r'%(col, tb[col].unit.__str__()))
                        print('type(tb[%r].data) = %r'%(col, type(tb[col].data)))
                        
        return tb
    
    def runPostProcessingCommands(self, table, postprocessing_commands, verbose=True):
        """Run postprocessing commands on an input table and output the result table.
        
        The postprocessing_commands should be a dictionary, where key is the column name and value is the command to evaluate and set to the column data.
        """
        tb = table
        if verbose:
            print('postprocessing table columns and rows')
        if not (isinstance(postprocessing_commands, dict) or isinstance(postprocessing_commands, configparser.SectionProxy)):
            print('type(postprocessing_commands)', type(postprocessing_commands))
            raise ValueError('postprocessing_commands should be a dictionary! Each key should be a column name of the table, and command should be an expression to eval().')
        for key, value in postprocessing_commands.items():
            col = key
            if re.match(r'^__([0-9]+)__ (.*)$', col):
                col = re.sub(r'^__([0-9]+)__ (.*)$', r'\2', col)
            if re.match(r'^tb\[\'(.*)\'\]$', col):
                col = re.sub(r'^tb\[\'(.*)\'\]$', r'\1', col)
            if isinstance(value, list):
                postprocessing_command_list = value
            else:
                postprocessing_command_list = [value]
            for postprocessing_command_one in postprocessing_command_list:
                if col == 'tb':
                    if verbose:
                        print('postprocessing table rows with command: %s'%(postprocessing_command_one))
                    tb = eval(postprocessing_command_one)
                else:
                    if verbose:
                        print('postprocessing table column %r with command: %s'%(col, postprocessing_command_one))
                    tb[col] = eval(postprocessing_command_one)
        return tb
    
    def queryTAP(self, server_url, table_name, column_key_values, query_command=None, column_unit_dict=None, postprocessing_commands=None, 
                 cache_dir=None, cache_name=None, verbose=True, overwrite=False):
        """Query TAP server with astroquery TAP.
        
        We will read the `self.catalog_meta_file`, an INI-format text file, and find the 
        TAP table name from the 'TABLE' key in the [TABLE] section, and table column names
        from the keys in the [COLUMNS] section. Mandatory keys should be ID, RA and DEC, 
        and keys like LOGMSTAR, LOGSFR, LOGSSFR, REDSHIFT, ZPHOT, ZSPEC can also be defined.
        Each key in the [COLUMNS] section should have a value that corresponds to the actual
        column name of the table in the TAP server. 
        
        This code will build a TAP/SQL query command and run an async query job to get the 
        result table from TAP server. If a 'QUERY_COMMAND' key is defined in the [TABLE] section
        in `self.catalog_meta_file`, then we will run that query command. 
        
        The returned table will contain ID, RA, DEC and other columns as defined in the 
        meta file `self.catalog_meta_file`, and will be saved as a compressed, FITS-format 
        catalog file named "table.fits.gz" under the `self.catalog_cache_dir` directory. 
        
        """
        # 
        # for TAP API, see -- https://astroquery.readthedocs.io/en/latest/utils/tap.html
        # 
        if self.iniparser is None:
            return None
        # 
        # check if enable cache or not
        enable_cache = False
        cache_fileroot = ''
        if cache_dir is not None and cache_name is not None:
            cache_fileroot = cache_dir+os.sep+cache_name
            enable_cache = True
        # 
        # check if do query or not
        do_query = True
        cache_filepath = ''
        if enable_cache:
            if os.path.isfile(cache_fileroot+'.fits.gz') and not overwrite:
                cache_filepath = cache_fileroot+'.fits.gz'
                do_query = False
            elif os.path.isfile(cache_fileroot+'.fits') and not overwrite:
                cache_filepath = cache_fileroot+'.fits'
                do_query = False
        # 
        # check if cache file exists
        if do_query:
            # 
            # build query command
            if query_command is not None and query_command != '':
                with open(cache_filepath+'_query_command.txt', 'w') as fp:
                    fp.write(query_command+'\n')
            else:
                query_command = self.buildQueryCommand(table=table_name, columns=column_key_values, 
                                                       cache_command=cache_fileroot+'_query_command.txt')
            # 
            # run query job
            if verbose:
                print('querying server url %s'%(server_url))
            job, tb = self.runQueryJob(query_command, server_url, 
                                      cache_table=cache_fileroot+'_cache.votable', 
                                      cache_jobid=cache_fileroot+'_query_jobid.txt', 
                                      cache_colnames=cache_fileroot+'_query_colnames.txt', 
                                      overwrite=overwrite)
            # 
            # rename columns
            tb = self.renameColumns(tb, column_key_values, verbose=verbose)
            # 
            # apply units if has input
            if column_unit_dict is not None:
                tb = self.applyColumnUnits(tb, column_unit_dict, verbose=verbose)
            # 
            # postprocessing if has input
            if postprocessing_commands is not None:
                tb = self.runPostProcessingCommands(tb, postprocessing_commands, verbose=verbose)
            # 
            # save to disk
            self.saveTableToDisk(tb, cache_fileroot+'.fits.gz', compression=True, remove_dump_files=cache_fileroot+'_cache*.votable')
        else:
            # 
            # read cached table
            if verbose:
                print('Reading cache "%s" (to requery TAP, set overwrite to True then rerun queryTAP)'%(cache_filepath))
            tb = Table.read(cache_filepath, format='fits')
        # 
        # return
        return tb
    
    def readTableFile(self, table_file, table_format, column_key_values, column_unit_dict=None, postprocessing_commands=None, 
                      cache_dir=None, cache_name=None, verbose=True, overwrite=False):
        """Read a table file and rename its column names according to the catalog meta info.
        
        """
        # 
        if self.iniparser is None:
            return None
        # 
        # check if enable cache or not
        enable_cache = False
        cache_fileroot = ''
        if cache_dir is not None and cache_name is not None:
            cache_fileroot = cache_dir+os.sep+cache_name
            enable_cache = True
        # 
        # check if do query or not
        do_query = True
        cache_filepath = ''
        if enable_cache:
            if os.path.isfile(cache_fileroot+'.fits.gz') and not overwrite:
                cache_filepath = cache_fileroot+'.fits.gz'
                do_query = False
            elif os.path.isfile(cache_fileroot+'.fits') and not overwrite:
                cache_filepath = cache_fileroot+'.fits'
                do_query = False
        # 
        # check if cache file exists
        if do_query:
            # 
            # read table file
            if verbose:
                print('reading table %s '%(table_file))
            if table_format == '':
                tb = Table.read(table_file)
            else:
                tb = Table.read(table_file, format=table_format)
                
            # 
            # rename columns
            tb = self.renameColumns(tb, column_key_values, verbose=verbose)
            # 
            # select columns
            if verbose:
                print('selecting columns')
            select_columns = list(column_key_values.keys())
            tb = tb[select_columns]
            # 
            # apply units if has input
            if column_unit_dict is not None:
                tb = self.applyColumnUnits(tb, column_unit_dict, verbose=verbose)
            # 
            # postprocessing if has input
            if postprocessing_commands is not None:
                tb = self.runPostProcessingCommands(tb, postprocessing_commands, verbose=verbose)
            # 
            # save to disk
            self.saveTableToDisk(tb, cache_fileroot+'.fits.gz', compression=True)
        else:
            # 
            # read cached table
            if verbose:
                print('Reading cache "%s" (to requery TAP, set overwrite to True then rerun queryTAP)'%(cache_filepath))
            tb = Table.read(cache_filepath, format='fits')
        # 
        # return
        return tb
    
    def evalConditionalDictionaryStr(self, input_str, key):
        """Evaluate a string or a dictionary string representative, return string or dictionary key value.
        
        This is useful to get a value by a conditional dictinary string representative. 
        For example, 
        ```
        evalConditionalDictionaryStr("{'*':SomeString, 'CASE_1':AnotherString, 'CASE_2':SecondString}", 'CASE_1')
        ```
        can be used to get a value for `'CASE_1'` from the conditional dictinary string representative, 
        which can be a key's value in an INI file. 
        
        If the input is not a dictionary, then return the string itself.
        
        """
        input_str = input_str.strip()
        output_val = None
        if re.match(r'^{.+}$', input_str):
            eval_dict = eval(input_str)
            for eval_key in eval_dict:
                #print('eval_dict eval_key', eval_key, 'key', key, 'fnmatch.fnmatch(key, eval_key)', fnmatch.fnmatch(key, eval_key))
                if eval_key != '*':
                    if eval_key.find('|'):
                        # regex
                        eval_matched = re.match(eval_key, key)
                    elif eval_key.find('*'):
                        # fnmatch
                        eval_matched = fnmatch.fnmatch(key, eval_key)
                    else:
                        # exact amtch
                        eval_matched = (key == eval_key)
                    # 
                    if eval_matched:
                        output_val = eval_dict[eval_key]
            # fallback
            if output_val is None and '*' in eval_dict:
                output_val = eval_dict['*']
        else:
            output_val = input_str
        return output_val
    
    def parseFilePath(self, filepath):
        if filepath.find('$catalog_from_papers') >= 0:
            filepath = filepath.replace('$catalog_from_papers', 
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                    'data', 'catalog_from_papers'))
        if filepath.find('$catalog_meta_info') >= 0:
            filepath = filepath.replace('$catalog_meta_info', 
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                    'data', 'catalog_meta_info'))
        if filepath.find('~') >= 0:
            filepath = os.path.expanduser(filepath)
        return filepath
    
    def setFilePath(self, filepath):
        """Set filepath, processing the string ~ or $ symbols.
        """
        self.file = self.parseFilePath(filepath)
    
    def loadTable(self, catalog_meta_file, catalog_cache_pool=None, verbose=True, overwrite=False):
        """Load a table by the input catalog meta file. 
        
        The input catalog meta file should be an INI-format text file that contains necessary information to define the table file path 
        and columns in it. It should contain a [TABLE] section, a [COLUMNS] section, and optionally [ASTROMETRY] and [PHOTOMETRY] sections.
        
        The [TABLE] section of the meta file should contain 'ACCESS', 'TAP' or 'FILE', and 'TABLE' keys. 
        The 'ACCESS' key can be either 'TAP' or 'FILE'. If 'ACCESS' is 'TAP', then the key 'TAP' should be defined to the server URL. 
        Or if 'ACCESS' is 'FILE', then the file path of the table should be defined in the 'FILE' key. 
        The 'Table' key should be the table name used for querying if the access method needs it. 
        
        This function is called at the construction of this class, so users do not need to call it by their own. 
        
        This function will read the table and try to fill in the following data ararys: 
            `self.ID`
            `self.RA`
            `self.DEC`
            `self.REDSHIFT`
            `self.ZPHOT`
            `self.ZSPEC`
            `self.REF_REDSHIFT`
            `self.REF_ZPHOT`
            `self.REF_ZSPEC`
            `self.LOGMSTAR`
            `self.E_LOGMSTAR`
            `self.REF_LOGMSTAR`
            `self.LOGMGAS`
            `self.E_LOGMGAS`
            `self.REF_LOGMGAS`
            `self.LOGMH2`
            `self.E_LOGMH2`
            `self.REF_LOGMH2`
            `self.LOGMHI`
            `self.E_LOGMHI`
            `self.REF_LOGMHI`
            `self.LOGSFR`
            `self.E_LOGSFR`
            `self.REF_LOGSFR`
            `self.LOGSSFR`
            `self.E_LOGSSFR`
            `self.REF_LOGSSFR`
            `self.LOGLUV`
            `self.E_LOGLUV`
            `self.REF_LOGLUV`
            `self.LOGLIR`
            `self.E_LOGLIR`
            `self.REF_LOGLIR`
            `self.FIELD`
        
        To correctly read those data arrays, correct column names should be defined under the [COLUMNS] section of the 
        input catalog meta file. For example, define the 'ID' key as the actual ID column name in the catalog, 
            ```
            [COLUMNS]
            ID = ACTUAL_ID_COLUMN_NAME
            RA = ACTUAL_RA_COLUMN_NAME
            DEC = ACTUAL_DEC_COLUMN_NAME
            REDSHIFT = ACTUAL_REDSHIFT_COLUMN_NAME
            LOGMSTAR = ACTUAL_STELLAR_MASS_COLUMN_NAME
            SFR = ACTUAL_SFR_COLUMN_NAME
            ```
        then the code will be able to read ID, RA, DEC, REDSHIFT, LOGMSTAR and LOGSFR. Note that in the above example 
        we can actually set the SFR key, and the code will take care of converting it to LOGSFR data array. 
        
        """
        # 
        # read the meta file
        self.catalog_meta_file = catalog_meta_file
        self.iniparser = CaseConfigParser(dict_type=MultiOrderedDict, strict=False, empty_lines_in_values=False, interpolation=None) # , converters={"list": MultiOrderedDict.getlist}
        self.iniparser.read(self.catalog_meta_file)
        # 
        # validate
        self.validateCatalogMetaInfo()
        # 
        # set the catalog_cache_dir
        if catalog_cache_pool is None:
            catalog_cache_pool = os.path.dirname(os.path.abspath(self.catalog_meta_file))
        catalog_cache_dir = catalog_cache_pool + os.sep + re.sub(r'\.ini$', r'', os.path.basename(self.catalog_meta_file)) + '_cache_dir'
        if not os.path.isdir(catalog_cache_dir):
            os.makedirs(catalog_cache_dir)
        self.catalog_cache_dir = catalog_cache_dir
        # 
        self.ref = self.iniparser['TABLE']['REF']
        # 
        # check if postprocessing_commands exist
        postprocessing_commands = None
        if 'POSTPROCESSING' in self.iniparser.sections():
            postprocessing_commands = self.iniparser['POSTPROCESSING']
        # 
        # read catalog table content
        self.access = self.iniparser['TABLE']['ACCESS']
        if self.access == 'TAP':
            # 
            # validated the meta info for TAP.
            self.validateCatalogMetaInfo(required_sections_keys={'TABLE':['TAP']})
            # 
            # get table name, column_key_values, etc
            table_name = self.iniparser['TABLE']['TABLE']
            server_url = self.iniparser['TABLE']['TAP']
            query_command = ''
            if 'QUERY_COMMAND' in self.iniparser['TABLE']:
                query_command = self.iniparser['TABLE']['QUERY_COMMAND']
            column_key_values = self.iniparser['COLUMNS']
            # 
            # run queryTAP
            self.table = self.queryTAP(server_url, table_name, column_key_values, query_command=query_command, postprocessing_commands=postprocessing_commands, 
                                       cache_dir=catalog_cache_dir, cache_name='table', 
                                       verbose=verbose, overwrite=overwrite)
            # 
        elif self.access == 'FILE':
            # 
            # validated the meta info for FILE.
            self.validateCatalogMetaInfo(required_sections_keys={'TABLE':['FILE']})
            self.setFilePath(self.iniparser['TABLE']['FILE'])
            # 
            # get table_file
            table_file = self.file
            table_format = ''
            if 'FORMAT' in self.iniparser['TABLE']:
                table_format = self.iniparser['TABLE']['FORMAT']
            if table_format == '' and table_file.endswith('.txt'):
                table_format = 'ascii.commented_header'
            column_key_values = self.iniparser['COLUMNS']
            # 
            # check table_file if it is a file name under the cache dir
            if (not os.path.isfile(table_file)) and os.path.isfile(os.path.join(catalog_cache_dir, table_file)):
                table_file = os.path.join(catalog_cache_dir, table_file)
            # 
            # read file
            self.table = self.readTableFile(table_file, table_format, column_key_values, postprocessing_commands=postprocessing_commands, 
                                            cache_dir=catalog_cache_dir, cache_name='table', 
                                            verbose=verbose, overwrite=overwrite)
            # 
        else:
            # 
            raise ValueError('ACCESS method %s is not accepted. It must be either TAP or FILE.'%(self.access))
        # 
        # read column data arrays
        self.colnames = self.table.colnames
        self.ID = self.getColumn('ID', ['NUMBER'], verbose=verbose)
        self.RA = self.getColumn('RA', ['ALPHA_J2000'], verbose=verbose)
        self.DEC = self.getColumn('DEC', ['DELTA_J2000', 'DE'], verbose=verbose)
        self.REDSHIFT = self.getColumn('REDSHIFT', ['Z', 'ZPHOT', 'ZPHOTO', 'PHOTOZ', 'ZPDF'], verbose=verbose)
        self.ZPHOT = self.getColumn('ZPHOT', ['ZPHOTO', 'PHOTOZ', 'ZPDF'], verbose=verbose)
        self.ZSPEC = self.getColumn('ZSPEC', ['SPECZ'], verbose=verbose)
        self.REF_REDSHIFT = self.getColumn('REF_REDSHIFT', ['REF_Z', 'REF_ZPHOT', 'REF_ZPHOTO', 'REF_PHOTOZ', 'REF_ZPDF'], verbose=verbose)
        self.REF_ZPHOT = self.getColumn('REF_ZPHOT', ['REF_ZPHOTO', 'REF_PHOTOZ', 'REF_ZPDF'], verbose=verbose)
        self.REF_ZSPEC = self.getColumn('REF_ZSPEC', ['REF_SPECZ'], verbose=verbose)
        self.QUALITY_ZSPEC = self.getColumn('QUALITY_ZSPEC', ['Q_Z', 'QZ', 'ZFLAGS'], verbose=verbose)
        self.LOGMSTAR = self.getColumn('LOGMSTAR', verbose=verbose)
        self.E_LOGMSTAR = self.getColumn('E_LOGMSTAR', verbose=verbose)
        self.REF_LOGMSTAR = self.getColumn('REF_LOGMSTAR', verbose=verbose)
        if self.LOGMSTAR is None:
            var = self.getColumn('MSTAR', verbose=verbose)
            if var is not None:
                self.LOGMSTAR = np.log10(var)
                var2 = self.getColumn('E_MSTAR', verbose=verbose)
                if var2 is not None:
                    self.E_LOGMSTAR = var2/var
        if self.LOGMSTAR is not None and self.E_LOGMSTAR is None:
            var16 = self.getColumn('LOGMSTAR_P16', verbose=verbose)
            var84 = self.getColumn('LOGMSTAR_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGMSTAR = np.abs(var84-var16)/2.0
        if self.LOGMSTAR is not None and self.E_LOGMSTAR is None:
            var16 = self.getColumn('MSTAR_P16', verbose=verbose)
            var84 = self.getColumn('MSTAR_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGMSTAR = np.abs(np.log10(var84)-np.log10(var16))/2.0
        # 
        self.LOGMGAS = self.getColumn('LOGMGAS', verbose=verbose)
        self.E_LOGMGAS = self.getColumn('E_LOGMGAS', verbose=verbose)
        self.REF_LOGMGAS = self.getColumn('REF_LOGMGAS', verbose=verbose)
        if self.LOGMGAS is None:
            var = self.getColumn('MGAS', verbose=verbose)
            if var is not None:
                self.LOGMGAS = np.log10(var)
        if self.LOGMGAS is not None and self.E_LOGMGAS is None:
            var16 = self.getColumn('LOGMGAS_P16', verbose=verbose)
            var84 = self.getColumn('LOGMGAS_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGMGAS = np.abs(var84-var16)/2.0
        if self.LOGMGAS is not None and self.E_LOGMGAS is None:
            var16 = self.getColumn('MGAS_P16', verbose=verbose)
            var84 = self.getColumn('MGAS_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGMGAS = np.abs(np.log10(var84)-np.log10(var16))/2.0
        # 
        self.LOGMH2 = self.getColumn('LOGMH2', ['LOGMMOL', 'LOGMMOLGAS'], verbose=verbose)
        self.E_LOGMH2 = self.getColumn('E_LOGMH2', ['E_LOGMMOL', 'E_LOGMMOLGAS'], verbose=verbose)
        self.REF_LOGMH2 = self.getColumn('REF_LOGMH2', ['REF_LOGMMOL', 'REF_LOGMMOLGAS'], verbose=verbose)
        if self.LOGMH2 is None:
            var = self.getColumn('MH2', ['MMOL', 'MMOLGAS'], verbose=verbose)
            if var is not None:
                self.LOGMH2 = np.log10(var)
                var2 = self.getColumn('E_MH2', ['E_MMOL', 'E_MMOLGAS'], verbose=verbose)
                if var2 is not None:
                    self.E_LOGMH2 = var2/var
        if self.LOGMH2 is not None and self.E_LOGMH2 is None:
            var16 = self.getColumn('LOGMH2_P16', verbose=verbose)
            var84 = self.getColumn('LOGMH2_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGMH2 = np.abs(var84-var16)/2.0
        if self.LOGMH2 is not None and self.E_LOGMH2 is None:
            var16 = self.getColumn('MH2_P16', verbose=verbose)
            var84 = self.getColumn('MH2_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGMH2 = np.abs(np.log10(var84)-np.log10(var16))/2.0
        # 
        self.LOGMHI = self.getColumn('LOGMHI', verbose=verbose)
        self.E_LOGMHI = self.getColumn('E_LOGMHI', verbose=verbose)
        self.REF_LOGMHI = self.getColumn('REF_LOGMHI', verbose=verbose)
        if self.LOGMHI is None:
            var = self.getColumn('MHI', verbose=verbose)
            if var is not None:
                self.LOGMHI = np.log10(var)
                var2 = self.getColumn('E_MHI', verbose=verbose)
                if var2 is not None:
                    self.E_LOGMHI = var2/var
        if self.LOGMHI is not None and self.E_LOGMHI is None:
            var16 = self.getColumn('LOGMHI_P16', verbose=verbose)
            var84 = self.getColumn('LOGMHI_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGMHI = np.abs(var84-var16)/2.0
        if self.LOGMHI is not None and self.E_LOGMHI is None:
            var16 = self.getColumn('MHI_P16', verbose=verbose)
            var84 = self.getColumn('MHI_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGMHI = np.abs(np.log10(var84)-np.log10(var16))/2.0
        # 
        self.LOGSFR = self.getColumn('LOGSFR', verbose=verbose)
        self.E_LOGSFR = self.getColumn('E_LOGSFR', verbose=verbose)
        self.REF_LOGSFR = self.getColumn('REF_LOGSFR', verbose=verbose)
        if self.LOGSFR is None:
            var = self.getColumn('SFR', verbose=verbose)
            if var is not None:
                self.LOGSFR = np.log10(var)
                var2 = self.getColumn('E_SFR', verbose=verbose)
                if var2 is not None:
                    self.E_LOGSFR = var2/var
        if self.LOGSFR is not None and self.E_LOGSFR is None:
            var16 = self.getColumn('LOGSFR_P16', verbose=verbose)
            var84 = self.getColumn('LOGSFR_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGSFR = np.abs(var84-var16)/2.0
        if self.LOGSFR is not None and self.E_LOGSFR is None:
            var16 = self.getColumn('SFR_P16', verbose=verbose)
            var84 = self.getColumn('SFR_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGSFR = np.abs(np.log10(var84)-np.log10(var16))/2.0
        # 
        self.LOGSSFR = self.getColumn('LOGSSFR', verbose=verbose)
        self.E_LOGSSFR = self.getColumn('E_LOGSSFR', verbose=verbose)
        self.REF_LOGSSFR = self.getColumn('REF_LOGSSFR', verbose=verbose)
        if self.LOGSSFR is None:
            var = self.getColumn('SSFR', verbose=verbose)
            if var is not None:
                self.LOGSSFR = np.log10(var)
                var2 = self.getColumn('E_SSFR', verbose=verbose)
                if var2 is not None:
                    self.E_LOGSSFR = var2/var
        if self.LOGSSFR is not None and self.E_LOGSSFR is None:
            var16 = self.getColumn('LOGSSFR_P16', verbose=verbose)
            var84 = self.getColumn('LOGSSFR_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGSSFR = np.abs(var84-var16)/2.0
        if self.LOGSSFR is not None and self.E_LOGSSFR is None:
            var16 = self.getColumn('SSFR_P16', verbose=verbose)
            var84 = self.getColumn('SSFR_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGSSFR = np.abs(np.log10(var84)-np.log10(var16))/2.0
        # 
        self.LOGLUV = self.getColumn('LOGLUV', verbose=verbose)
        self.E_LOGLUV = self.getColumn('E_LOGLUV', verbose=verbose)
        self.REF_LOGLUV = self.getColumn('REF_LOGLUV', verbose=verbose)
        if self.LOGLUV is None:
            var = self.getColumn('LIR', ['LIR','L_IR'], verbose=verbose)
            if var is not None:
                self.LOGLUV = np.log10(var)
                var2 = self.getColumn('E_LIR', ['E_LIR','E_L_IR'], verbose=verbose)
                if var2 is not None:
                    self.E_LOGLUV = var2/var
        if self.LOGLUV is not None and self.E_LOGLUV is None:
            var16 = self.getColumn('LOGLUV_P16', verbose=verbose)
            var84 = self.getColumn('LOGLUV_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGLUV = np.abs(var84-var16)/2.0
        if self.LOGLUV is not None and self.E_LOGLUV is None:
            var16 = self.getColumn('LUV_P16', verbose=verbose)
            var84 = self.getColumn('LUV_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGLUV = np.abs(np.log10(var84)-np.log10(var16))/2.0
        # 
        self.LOGLIR = self.getColumn('LOGLIR', verbose=verbose)
        self.E_LOGLIR = self.getColumn('E_LOGLIR', verbose=verbose)
        self.REF_LOGLIR = self.getColumn('REF_LOGLIR', verbose=verbose)
        if self.LOGLIR is None:
            var = self.getColumn('LIR', ['LIR','L_IR'], verbose=verbose)
            if var is not None:
                self.LOGLIR = np.log10(var)
                var2 = self.getColumn('E_LIR', ['E_LIR','E_L_IR'], verbose=verbose)
                if var2 is not None:
                    self.E_LOGLIR = var2/var
        if self.LOGLIR is not None and self.E_LOGLIR is None:
            var16 = self.getColumn('LOGLIR_P16', verbose=verbose)
            var84 = self.getColumn('LOGLIR_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGLIR = np.abs(var84-var16)/2.0
        if self.LOGLIR is not None and self.E_LOGLIR is None:
            var16 = self.getColumn('LIR_P16', verbose=verbose)
            var84 = self.getColumn('LIR_P84', verbose=verbose)
            if var16 is not None and var84 is not None:
                self.E_LOGLIR = np.abs(np.log10(var84)-np.log10(var16))/2.0
        # 
        self.FIELD = self.getColumn('FIELD', verbose=verbose)
        # 
        # 
        # 
        # also query/read photometry if the 'PHOTOMETRY' section exists
        if 'PHOTOMETRY' in self.iniparser:
            # 
            # validated the meta info for photometry section.
            self.validateCatalogMetaInfo(required_sections_keys={'PHOTOMETRY':['ID','RA','DEC','BANDS','FILTERS','WAVELENGTHS','FLUX_UNIT']})
            # 
            bands = self.iniparser['PHOTOMETRY']['BANDS']
            filters = self.iniparser['PHOTOMETRY']['FILTERS']
            wavelengths = self.iniparser['PHOTOMETRY']['WAVELENGTHS']
            bands = eval(bands)
            filters = eval(filters)
            wavelengths = eval(wavelengths)
            flux_unit_str = self.iniparser['PHOTOMETRY']['FLUX_UNIT'] # <TODO> FLUX_UNIT can be a list, a string or a expression
            # 
            column_key_values = OrderedDict()
            column_key_values['ID'] = self.iniparser['PHOTOMETRY']['ID']
            column_key_values['RA'] = self.iniparser['PHOTOMETRY']['RA']
            column_key_values['DEC'] = self.iniparser['PHOTOMETRY']['DEC']
            filter_wavelength_dict = OrderedDict()
            flux_unit_dict = OrderedDict()
            flux_unit_list = []
            if flux_unit_str.find('[') >= 0:
                flux_unit_list = eval(flux_unit_str)
            elif flux_unit_str.find('u.') >= 0:
                flux_unit_list = [eval(flux_unit_str)]*len(bands)
            elif flux_unit_str.strip() == '':
                flux_unit_list = ['']*len(bands)
            else:
                flux_unit_list = [u.Unit(flux_unit_str)]*len(bands)
            # loop each band
            # note that we do not check the array lengths of bands, filters, wavelengths and fluxunits
            for this_band, this_filter, this_wavelength, this_fluxunit in list(zip(bands, filters, wavelengths, flux_unit_list)):
                filter_wavelength_dict[this_filter] = this_wavelength
                this_flux_colname = this_band
                this_fluxerr_colname = this_band
                if 'FLUX_PREFIX' in self.iniparser['PHOTOMETRY']:
                    this_flux_prefix = self.evalConditionalDictionaryStr(self.iniparser['PHOTOMETRY']['FLUX_PREFIX'], key=this_band)
                    this_flux_colname = this_flux_prefix + this_flux_colname
                if 'FLUX_SUFFIX' in self.iniparser['PHOTOMETRY']:
                    this_flux_suffix = self.evalConditionalDictionaryStr(self.iniparser['PHOTOMETRY']['FLUX_SUFFIX'], key=this_band)
                    this_flux_colname = this_flux_colname + this_flux_suffix
                if 'FLUXERR_PREFIX' in self.iniparser['PHOTOMETRY']:
                    this_fluxerr_prefix = self.evalConditionalDictionaryStr(self.iniparser['PHOTOMETRY']['FLUXERR_PREFIX'], key=this_band)
                    this_fluxerr_colname = this_fluxerr_prefix + this_fluxerr_colname
                if 'FLUXERR_SUFFIX' in self.iniparser['PHOTOMETRY']:
                    this_fluxerr_suffix = self.evalConditionalDictionaryStr(self.iniparser['PHOTOMETRY']['FLUXERR_SUFFIX'], key=this_band)
                    this_fluxerr_colname = this_fluxerr_colname + this_fluxerr_suffix
                column_key_values['FLUX '+this_filter] = this_flux_colname
                flux_unit_dict['FLUX '+this_filter] = this_fluxunit
                if this_fluxerr_colname != this_flux_colname:
                    column_key_values['FLUXERR '+this_filter] = this_fluxerr_colname
                    flux_unit_dict['FLUXERR '+this_filter] = this_fluxunit
            if verbose:
                print('column_key_values: ', column_key_values)
                print('filter_wavelength_dict: ', filter_wavelength_dict)
                print('flux_unit_dict: ', flux_unit_dict)
            # 
            if not os.path.isfile(catalog_cache_dir+os.sep+'photometry_filter_wavelength_dict.json') or overwrite:
                with open(catalog_cache_dir+os.sep+'photometry_filter_wavelength_dict.json', 'w') as fp:
                    json.dump(filter_wavelength_dict, fp, indent=4)
                if verbose:
                    print('Output to "%s"'%(catalog_cache_dir+os.sep+'photometry_filter_wavelength_dict.json'))
            # 
            photometry_access = self.access
            if 'ACCESS' in self.iniparser['PHOTOMETRY']:
                photometry_access = self.iniparser['PHOTOMETRY']['ACCESS']
            if verbose:
                print('photometry_access: %s'%(photometry_access))
            # 
            if photometry_access == 'TAP':
                # 
                # get specifc table name for photometry if needed
                if 'TABLE' in self.iniparser['PHOTOMETRY']:
                    table_name = self.iniparser['PHOTOMETRY']['TABLE']
                if 'TAP' in self.iniparser['PHOTOMETRY']:
                    server_url = self.iniparser['PHOTOMETRY']['TAP']
                query_command = ''
                if 'QUERY_COMMAND' in self.iniparser['PHOTOMETRY']:
                    query_command = self.iniparser['PHOTOMETRY']['QUERY_COMMAND']
                # 
                # run queryTAP
                self.table = self.queryTAP(server_url, table_name, column_key_values, query_command=query_command, column_unit_dict=flux_unit_dict, 
                                           cache_dir=catalog_cache_dir, cache_name='photometry', 
                                           verbose=verbose, overwrite=overwrite)
                # 
            elif photometry_access == 'FILE':
                # 
                # get specifc table file for photometry if needed
                if 'FILE' in self.iniparser['PHOTOMETRY']:
                    table_file = self.parseFilePath(self.iniparser['PHOTOMETRY']['FILE'])
                if 'FORMAT' in self.iniparser['PHOTOMETRY']:
                    table_format = self.iniparser['PHOTOMETRY']['FORMAT']
                elif 'FORMAT' in self.iniparser['TABLE']:
                    table_format = self.iniparser['PHOTOMETRY']['FORMAT']
                else:
                    table_format = ''
                if table_format == '' and table_file.endswith('.txt'):
                    table_format = 'ascii.commented_header'
                # 
                # check table_file if it is a file name under the cache dir
                if (not os.path.isfile(table_file)) and os.path.isfile(os.path.join(catalog_cache_dir, table_file)):
                    table_file = os.path.join(catalog_cache_dir, table_file)
                # 
                # read file
                self.table = self.readTableFile(table_file, table_format, column_key_values, column_unit_dict=flux_unit_dict, 
                                                cache_dir=catalog_cache_dir, cache_name='photometry', 
                                                verbose=verbose, overwrite=overwrite)
                # 
            else:
                # 
                raise ValueError('ACCESS method %s for PHOTOMETRY is not accepted. It must be either TAP or FILE.'%(photometry_access))
        # 
        # 
        # 
        # also query/read spectroscopy if the 'SPECTROSCOPY' section exists
        if 'SPECTROSCOPY' in self.iniparser:
            # 
            # validated the meta info for spectroscopy section.
            self.validateCatalogMetaInfo(required_sections_keys={'SPECTROSCOPY':
                ['ID','RA','DEC',
                 'LINE_NAME',
                 'LINE_FLUX','LINE_VEL','LINE_SIG',
                 'FLUX_UNIT','VEL_UNIT','SIG_UNIT','SIG_TYPE']})
            # 
            line_names = self.iniparser['SPECTROSCOPY']['LINE_NAME']
            line_flux_columns = self.iniparser['SPECTROSCOPY']['LINE_FLUX']
            line_vel_columns = self.iniparser['SPECTROSCOPY']['LINE_VEL']
            line_sig_columns = self.iniparser['SPECTROSCOPY']['LINE_SIG']
            line_names = eval(line_names)
            line_flux_columns = eval(line_flux_columns)
            line_vel_columns = eval(line_vel_columns)
            line_sig_columns = eval(line_sig_columns)
            flux_unit_str = self.iniparser['SPECTROSCOPY']['FLUX_UNIT'] # <TODO> FLUX_UNIT can be a list, a string or a expression
            vel_unit_str = self.iniparser['SPECTROSCOPY']['VEL_UNIT'] # <TODO> VEL_UNIT can be a list, a string or a expression
            sig_unit_str = self.iniparser['SPECTROSCOPY']['SIG_UNIT'] # <TODO> SIG_UNIT can be a list, a string or a expression
            sig_type_str = self.iniparser['SPECTROSCOPY']['SIG_TYPE'] # <TODO> SIG_TYPE can be a list, a string or a expression
            # 
            column_key_values = OrderedDict()
            column_key_values['ID'] = self.iniparser['SPECTROSCOPY']['ID']
            column_key_values['RA'] = self.iniparser['SPECTROSCOPY']['RA']
            column_key_values['DEC'] = self.iniparser['SPECTROSCOPY']['DEC']
            column_unit_dict = OrderedDict()
            # 
            flux_unit_list = []
            if flux_unit_str.find('[') >= 0:
                flux_unit_list = eval(flux_unit_str)
            elif flux_unit_str.find('u.') >= 0:
                flux_unit_list = [eval(flux_unit_str)]*len(line_flux_columns)
            elif flux_unit_str.strip() == '':
                flux_unit_list = ['']*len(line_flux_columns)
            else:
                flux_unit_list = [u.Unit(flux_unit_str)]*len(line_flux_columns)
            # 
            vel_unit_list = []
            if vel_unit_str.find('[') >= 0:
                vel_unit_list = eval(vel_unit_str)
            elif vel_unit_str.find('u.') >= 0:
                vel_unit_list = [eval(vel_unit_str)]*len(line_flux_columns)
            elif vel_unit_str.strip() == '':
                vel_unit_list = ['']*len(line_flux_columns)
            else:
                vel_unit_list = [u.Unit(vel_unit_str)]*len(line_flux_columns)
            # 
            sig_unit_list = []
            if sig_unit_str.find('[') >= 0:
                sig_unit_list = eval(sig_unit_str)
            elif sig_unit_str.find('u.') >= 0:
                sig_unit_list = [eval(sig_unit_str)]*len(line_flux_columns)
            elif sig_unit_str.strip() == '':
                sig_unit_list = ['']*len(line_flux_columns)
            else:
                sig_unit_list = [u.Unit(sig_unit_str)]*len(line_flux_columns)
            # 
            sig_type_dict = OrderedDict()
            sig_type_list = []
            if sig_type_str.find('[') >= 0:
                sig_type_list = eval(sig_type_str)
            elif sig_type_str.strip() == '':
                sig_type_list = ['']*len(line_flux_columns)
            else:
                sig_type_list = [str(sig_type_str).strip()]*len(line_flux_columns)
            # 
            # loop each band
            # note that we do not check the array lengths of line_flux_columns, line_vel_columns, line_sig_columns and fluxunits
            for this_line_name, this_flux_col, this_vel_col, this_sig_col, this_flux_unit, this_vel_unit, this_sig_unit, this_sig_type in \
                    list(zip(line_names, line_flux_columns, line_vel_columns, line_sig_columns, flux_unit_list, vel_unit_list, sig_unit_list, sig_type_list)):
                # 
                this_flux_colname = this_flux_col
                this_fluxerr_colname = this_flux_col
                if 'FLUX_PREFIX' in self.iniparser['SPECTROSCOPY']:
                    this_flux_prefix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['FLUX_PREFIX'], key=this_flux_col)
                    this_flux_colname = this_flux_prefix + this_flux_colname
                if 'FLUX_SUFFIX' in self.iniparser['SPECTROSCOPY']:
                    this_flux_suffix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['FLUX_SUFFIX'], key=this_flux_col)
                    this_flux_colname = this_flux_colname + this_flux_suffix
                if 'FLUXERR_PREFIX' in self.iniparser['SPECTROSCOPY']:
                    this_fluxerr_prefix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['FLUXERR_PREFIX'], key=this_flux_col)
                    this_fluxerr_colname = this_fluxerr_prefix + this_fluxerr_colname
                if 'FLUXERR_SUFFIX' in self.iniparser['SPECTROSCOPY']:
                    this_fluxerr_suffix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['FLUXERR_SUFFIX'], key=this_flux_col)
                    this_fluxerr_colname = this_fluxerr_colname + this_fluxerr_suffix
                column_key_values['LINE FLUX '+this_line_name] = this_flux_colname
                column_unit_dict['LINE FLUX '+this_line_name] = this_flux_unit
                if this_fluxerr_colname != this_flux_colname:
                    column_key_values['LINE FLUXERR '+this_line_name] = this_fluxerr_colname
                    column_unit_dict['LINE FLUXERR '+this_line_name] = this_flux_unit
                # 
                if this_vel_col != '':
                    this_vel_colname = this_vel_col
                    this_velerr_colname = this_vel_col
                    if 'VEL_PREFIX' in self.iniparser['SPECTROSCOPY']:
                        this_vel_prefix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['VEL_PREFIX'], key=this_vel_col)
                        this_vel_colname = this_vel_prefix + this_vel_colname
                    if 'VEL_SUFFIX' in self.iniparser['SPECTROSCOPY']:
                        this_vel_suffix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['VEL_SUFFIX'], key=this_vel_col)
                        this_vel_colname = this_vel_colname + this_vel_suffix
                    if 'VELERR_PREFIX' in self.iniparser['SPECTROSCOPY']:
                        this_velerr_prefix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['VELERR_PREFIX'], key=this_vel_col)
                        this_velerr_colname = this_velerr_prefix + this_velerr_colname
                    if 'VELERR_SUFFIX' in self.iniparser['SPECTROSCOPY']:
                        this_velerr_suffix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['VELERR_SUFFIX'], key=this_vel_col)
                        this_velerr_colname = this_velerr_colname + this_velerr_suffix
                    column_key_values['LINE VEL '+this_line_name] = this_vel_colname
                    column_unit_dict['LINE VEL '+this_line_name] = this_vel_unit
                    if this_velerr_colname != this_vel_colname:
                        column_key_values['LINE VELERR '+this_line_name] = this_velerr_colname
                        column_unit_dict['LINE VELERR '+this_line_name] = this_vel_unit
                # 
                if this_sig_col != '':
                    this_sig_colname = this_sig_col
                    this_sigerr_colname = this_sig_col
                    if 'SIG_PREFIX' in self.iniparser['SPECTROSCOPY']:
                        this_sig_prefix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['SIG_PREFIX'], key=this_sig_col)
                        this_sig_colname = this_sig_prefix + this_sig_colname
                    if 'SIG_SUFFIX' in self.iniparser['SPECTROSCOPY']:
                        this_sig_suffix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['SIG_SUFFIX'], key=this_sig_col)
                        this_sig_colname = this_sig_colname + this_sig_suffix
                    if 'SIGERR_PREFIX' in self.iniparser['SPECTROSCOPY']:
                        this_sigerr_prefix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['SIGERR_PREFIX'], key=this_sig_col)
                        this_sigerr_colname = this_sigerr_prefix + this_sigerr_colname
                    if 'SIGERR_SUFFIX' in self.iniparser['SPECTROSCOPY']:
                        this_sigerr_suffix = self.evalConditionalDictionaryStr(self.iniparser['SPECTROSCOPY']['SIGERR_SUFFIX'], key=this_sig_col)
                        this_sigerr_colname = this_sigerr_colname + this_sigerr_suffix
                    column_key_values['LINE SIG '+this_line_name] = this_sig_colname
                    column_unit_dict['LINE SIG '+this_line_name] = this_sig_unit
                    sig_type_dict['LINE SIG '+this_line_name] = this_sig_type # needed for line sigma FWHM to sigma conversion
                    if this_sigerr_colname != this_sig_colname:
                        column_key_values['LINE SIGERR '+this_line_name] = this_sigerr_colname
                        column_unit_dict['LINE SIGERR '+this_line_name] = this_sig_unit
                        sig_type_dict['LINE SIGERR '+this_line_name] = this_sig_type # needed for line sigma FWHM to sigma conversion
            # 
            if verbose:
                print('column_key_values: ', column_key_values)
                print('column_unit_dict: ', column_unit_dict)
                print('sig_type_dict: ', sig_type_dict)
            # 
            spectroscopy_access = self.access
            if 'ACCESS' in self.iniparser['SPECTROSCOPY']:
                spectroscopy_access = self.iniparser['SPECTROSCOPY']['ACCESS']
            if verbose:
                print('spectroscopy_access: %s'%(spectroscopy_access))
            # 
            if spectroscopy_access == 'TAP':
                # 
                # get specifc table name for spectroscopy if needed
                if 'TABLE' in self.iniparser['SPECTROSCOPY']:
                    table_name = self.iniparser['SPECTROSCOPY']['TABLE']
                if 'TAP' in self.iniparser['SPECTROSCOPY']:
                    server_url = self.iniparser['SPECTROSCOPY']['TAP']
                query_command = ''
                if 'QUERY_COMMAND' in self.iniparser['SPECTROSCOPY']:
                    query_command = self.iniparser['SPECTROSCOPY']['QUERY_COMMAND']
                # 
                # run queryTAP
                self.table = self.queryTAP(server_url, table_name, column_key_values, query_command=query_command, column_unit_dict=column_unit_dict, 
                                           cache_dir=catalog_cache_dir, cache_name='spectroscopy', 
                                           verbose=verbose, overwrite=overwrite)
                # 
            elif spectroscopy_access == 'FILE':
                # 
                # get specifc table file for spectroscopy if needed
                if 'FILE' in self.iniparser['SPECTROSCOPY']:
                    table_file = self.parseFilePath(self.iniparser['SPECTROSCOPY']['FILE'])
                if 'FORMAT' in self.iniparser['SPECTROSCOPY']:
                    table_format = self.iniparser['SPECTROSCOPY']['FORMAT']
                elif 'FORMAT' in self.iniparser['TABLE']:
                    table_format = self.iniparser['SPECTROSCOPY']['FORMAT']
                else:
                    table_format = ''
                if table_format == '' and table_file.endswith('.txt'):
                    table_format = 'ascii.commented_header'
                # 
                # check table_file if it is a file name under the cache dir
                if (not os.path.isfile(table_file)) and os.path.isfile(os.path.join(catalog_cache_dir, table_file)):
                    table_file = os.path.join(catalog_cache_dir, table_file)
                # 
                # read file
                self.table = self.readTableFile(table_file, table_format, column_key_values, column_unit_dict=column_unit_dict, 
                                                cache_dir=catalog_cache_dir, cache_name='spectroscopy', 
                                                verbose=verbose, overwrite=overwrite)
                # 
            else:
                # 
                raise ValueError('ACCESS method %s for SPECTROSCOPY is not accepted. It must be either TAP or FILE.'%(spectroscopy_access))
            # 
            # post-process line sigma FWHM to sigma conversion
            if len(sig_type_dict) > 0:
                for key in sig_type_dict:
                    this_sig_type = sig_type_dict[key]
                    if this_sig_type.upper().find('FWHM') >= 0:
                        if verbose:
                            print('converting FHWM to sigma by dividing 2.35482: ', key)
                        self.table[key] /= 2.35482
        # 
        # 
        # 
        # return
        return
    
    def getColumn(self, column_name, alternative_column_names=None, verbose=True, warning=False):
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
                if verbose:
                    print('Reading column %s'%(matched_colname))
                return self.table[matched_colname]
            else:
                if verbose and warning:
                    print('Warning! Column %r was not found in the table %r (%s)!'%(column_name, self.catalog_meta_file, re.sub(r'[ \t\r\n]+', r' ', str(self.colnames))))
        return None
    
    def getPhotometryByID(self, ID):
        if self.table is not None and self.iniparser is not None:
            if 'PHOTOMETRY' in self.iniparser.sections():
                check_ok = True
                for key in ['BANDS', 'FILTERS', 'WAVELENGTHS', 'FLUX_CONV', 'FLUX_PREFIX', 'FLUXERR_PREFIX']:
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
                for key in ['BANDS', 'FILTERS', 'WAVELENGTHS', 'FLUX_CONV', 'FLUX_PREFIX', 'FLUXERR_PREFIX']:
                    if key not in self.iniparser['PHOTOMETRY']:
                        print('Error! The input catalog meta file should contain key %s in the [PHOTOMETRY] section!'%(key))
                        check_ok = False
                if not check_ok:
                    print('Error! The input catalog meta file %r seem to be invalid!'%(self.catalog_meta_file))
                    raise Exception('Error! The input catalog meta file %r seem to be invalid!'%(self.catalog_meta_file))
                # 
                pass
    




