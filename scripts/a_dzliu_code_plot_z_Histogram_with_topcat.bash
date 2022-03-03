#!/bin/bash
# 
set -e

topcat -stilts plot2plane \
   xpix=713 ypix=511 \
   xlabel=z ylabel=N fontsize=20 \
   xmin=0 xmax=10.16 ylog=true \
   legend=true legpos=0.989,0.980 \
   in=master_catalog_single_entry_more_columns.fits \
   binsize=+0.2 \
   layer1=Histogram \
      x1=z leglabel1='All' \
   layer2=Histogram \
      x2=z leglabel2='zspec' \
      icmd2='select "(zspec>0.0 && parseFloat(Qzspec)>0.0)"' \
      color2=blue \
    out='Plot_z_Histogram.pdf'

convert -density 200 -alpha remove 'Plot_z_Histogram.pdf' 'Plot_z_Histogram.png'


