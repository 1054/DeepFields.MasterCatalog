#!/bin/bash
# 
set -e

fields=(aegis cosmos goodsn goodss uds)
versions=(4.1 4.1 4.1 4.1 4.2)
for (( i = 0; i < ${#fields[@]}; i++ )); do
    field="${fields[i]}"
    v="v${versions[i]}"
    if [[ ! -f ${field}_3dhst.${v}.cats.all.in.one.FITS ]]; then
    topcat -stilts tmatchn nin=4 \
        in1=${field}_3dhst.${v}.cats/Catalog/${field}_3dhst.${v}.cat.FITS \
        in2=${field}_3dhst.${v}.cats/Eazy/${field}_3dhst.${v}.zout.FITS \
        in3=${field}_3dhst.${v}.cats/Fast/${field}_3dhst.${v}.fout.FITS \
        in4=${field}_3dhst.${v}.cats/RF_colors/${field}_3dhst.${v}.master.RF.FITS \
        values1='id' values2='id' values3='id' values4='id' \
        suffix1='' suffix2='_2' suffix3='_3' suffix4='_4' \
        matcher=exact fixcols=dups \
        ocmd="addcol field \"\\\"$(echo ${field} | tr [:lower:] [:upper:])\\\"\"" \
        out=${field}_3dhst.${v}.cats.all.in.one.FITS
    fi
done
