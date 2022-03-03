#!/bin/bash
# 
set -e

topcat -stilts tpipe \
   in=master_catalog_single_entry_more_columns.fits \
   cmd='addcol FLAG_HAS_VALID_ZSPEC "(zspec>0.0 && parseFloat(Qzspec)>0.0)"' \
   cmd='select "FLAG_HAS_VALID_ZSPEC"' \
   omode=stats



