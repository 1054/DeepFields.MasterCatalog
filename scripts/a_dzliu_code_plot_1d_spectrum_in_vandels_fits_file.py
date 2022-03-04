#!/usr/bin/env python
# 
"""This script is used to plot the 1D spectrum from the VANDELS survey data.


VANDELS survey: 
http://vandels.inaf.it/dr4.html

VANDELS data release readme:
Spectra are stored as multi-extension FITS files containing the following extensions;
Primary: the 1D extracted spectrum
EXR2D: the 2D linearly resampled spectrum
SKY: the 1D sky spectrum
NOISE: the 1D noise estimate
EXR1D: a copy of the 1D extracted spectrum (to recover any edit that might be done on the Primary)
THUMB: the image thumbnail of the object
EXR1D_UNCORR: the original 1D spectrum without the correction that was applied to the originally 
calibrated spectra, due to a systematic drop in flux at the very blue end of the spectra, compared 
to the available broad band photometryEach extension can be viewed using standard tools like IRAF 
or IDL. The full information stored in these files can be inspected as a whole using the pandora.ez 
software as shown in this SCREENSHOT. If you want to install this tool follow the instructions 
at this LINK (see VANDELS survey website). 

"""

import os, sys, re
import numpy as np
from astropy.io import fits
import astropy.units as u
import matplotlib as mpl
import matplotlib.pyplot as plt
from collections import OrderedDict

fits_file = 'id_3dhst_v4_uds_21272/sc_UDS012744_P2M1Q2_P2M2Q2_P2M3Q2_P2M4Q2_011_3.fits'
sci_spectrum_data, sci_header = fits.getdata(fits_file, header=True)
sky_spectrum_data = fits.getdata(fits_file, ext=2)
err_spectrum_data = fits.getdata(fits_file, ext=3)

#z = 5.4106
#z = 2.8014
z = 2.532

xarray = ((np.arange(sci_header['NAXIS1'])+1)-sci_header['CRPIX1'])*sci_header['CDELT1'] + sci_header['CRVAL1']
xarray = xarray * u.angstrom
ymin = np.nanmin(sci_spectrum_data)
ymax = np.nanmax(sci_spectrum_data)


fig = plt.figure(figsize=(16.0, 3.6))
ax = fig.add_subplot(1, 1, 1)
fig.subplots_adjust(left=0.05, right=0.97, bottom=0.14, top=0.93)
ax.tick_params(axis='both', direction='in', top=True, right=True)
ax.plot(xarray, sci_spectrum_data, lw=0.6, label='sci')
ax.plot(xarray, err_spectrum_data, lw=0.6, color='red', alpha=0.8, label='err')
ax.legend(loc='upper right')
ax.set_ylim([ymin, ymax+0.08*(ymax-ymin)])
ax.set_xlabel(r'Wavelength [$\AA$]', fontsize=12)
ax.grid(True, color='#888888', ls='dotted', lw=0.25, alpha=0.5)

line_dict = OrderedDict()
line_dict['H-beta' ]      = 4861.36300
line_dict['[OIII]']       = 4958.91100
#line_dict['[OIII]']       = 5006.84300
line_dict['[NII]']        = 6548.05000
line_dict['H-alpha']      = 6562.80100
line_dict['[NII]']        = 6583.45000
#line_dict['[SII]']        = 6716.44000
#line_dict['[SII]']        = 6730.82000
#line_dict['[OII]']        = 3726.03000
line_dict['[OII]']        = 3728.82000
#line_dict['[MgII]']       = 2798.00000
line_dict['Ly-alpha']     = 1216.00000
line_dict['Lyman-break']  = 912.00000
for key in line_dict:
    ax.annotate(key, xy=(line_dict[key]*(1.+z), ymax-0.1*(ymax-ymin)), xytext=(line_dict[key]*(1.+z), ymax), 
                ha='center', arrowprops={'arrowstyle':'->'})

ax.text(0.90, 0.95, r'$z=%g$'%(z), ha='right', va='top', transform=ax.transAxes, fontsize=12)

output_figure = re.sub(r'\.fits', r'', fits_file) + '.spectrum.z.%s'%(z)
fig.savefig(output_figure+'.pdf', dpi=300, transparent=True)
fig.savefig(output_figure+'.png', dpi=300, transparent=True)
print('Output to "%s"'%(output_figure+'.pdf'))
