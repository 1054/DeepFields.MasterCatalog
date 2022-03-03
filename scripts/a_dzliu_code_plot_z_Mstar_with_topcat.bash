#!/bin/bash
# 
set -e

topcat -stilts plot2plane \
   xpix=713 ypix=511 \
   xlabel=z ylabel=logMstar fontsize=20 \
   xmin=0 xmax=10.16 ymin=0.1 ymax=14.9 \
   legend=true legpos=0.989,0.036 \
   in=master_catalog_single_entry_more_columns.fits \
   layer1=Mark \
      x1=z y1=logMstar leglabel1='All' \
      shading1=auto \
   layer2=Mark \
      x2=z y2=logMstar leglabel2='zspec' \
      icmd2='select "zspec>0.0"' \
      color2=blue \
      shading2=auto \
    out='Plot_z_Mstar.pdf'

convert -density 200 -alpha remove 'Plot_z_Mstar.pdf' 'Plot_z_Mstar.png'


