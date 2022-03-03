#!/bin/bash
# 

script_dir=$(dirname $(dirname "${BASH_SOURCE[0]}"))


# prepare catalog meta info (needs manually collecting catalogs and preparing the *.ini files)
$script_dir/pipeline-make-deep-field-master-catalog 1 1 1


# make sure you have set the make_master_catalog python script up to date
ls pipeline/1_constructing_master_catalog/2_constructing_master_catalog/1_make_master_catalog_multi_entries.py


# construct the master catalog
$script_dir/pipeline-make-deep-field-master-catalog 1 2 1



