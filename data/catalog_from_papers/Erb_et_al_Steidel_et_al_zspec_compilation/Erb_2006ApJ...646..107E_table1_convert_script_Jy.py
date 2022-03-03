#!/usr/bin/env python
# 

import numpy as np
import astropy
import astropy.units as u
from astropy.table import Table
from astropy.coordinates import SkyCoord, FK5
from collections import OrderedDict
import synphot
from synphot import SourceSpectrum
# see -- https://synphot.readthedocs.io/en/latest/synphot/units.html
# synphot.units.VEGAMAG


tb = Table.read('Erb_2006ApJ...646..107E_table1_photometry.txt', format='ascii.commented_header')
skycoords = SkyCoord(tb['RA_HMS'], tb['DEC_DMS'], unit=(u.hour, u.deg), frame=FK5)
#  z       R       G_minus_R   U_minus_G  Ks   J_minus_Ks
tb['G'] = tb['R'] + tb['G_minus_R']
tb['U'] = tb['G'] + tb['U_minus_G']
tb['J'] = tb['Ks'] + tb['J_minus_Ks']

f_U = synphot.units.convert_flux(3550.0e-10*u.m, tb['U']*astropy.units.ABmag, synphot.units.FNU) # Steidel et al. 2003ApJ...592..728S Fig. 1.
f_G = synphot.units.convert_flux(4780.0e-10*u.m, tb['G']*astropy.units.ABmag, synphot.units.FNU) # Steidel et al. 2003ApJ...592..728S Fig. 1.
f_R = synphot.units.convert_flux(6830.0e-10*u.m, tb['R']*astropy.units.ABmag, synphot.units.FNU) # Steidel et al. 2003ApJ...592..728S Fig. 1.
f_J = synphot.units.convert_flux(1.25e-6*u.m, tb['J']*synphot.units.VEGAMAG, synphot.units.FNU, vegaspec=SourceSpectrum.from_vega()) # https://sites.astro.caltech.edu/palomar/observer/200inchResources/P200filters.html, WIRC
f_Ks = synphot.units.convert_flux(2.15e-6*u.m, tb['Ks']*synphot.units.VEGAMAG, synphot.units.FNU, vegaspec=SourceSpectrum.from_vega()) # https://sites.astro.caltech.edu/palomar/observer/200inchResources/P200filters.html, WIRC

f_U = f_U.to(u.Jy)
f_G = f_G.to(u.Jy)
f_R = f_R.to(u.Jy)
f_J = f_J.to(u.Jy)
f_Ks = f_Ks.to(u.Jy)

out_dict = OrderedDict()
out_dict['ID'] = tb['ID']
out_dict['RA'] = skycoords.ra.deg
out_dict['DEC'] = skycoords.dec.deg
out_dict['z'] = tb['z']

out_dict['FLUX_U'] = f_U
out_dict['FLUXERR_U'] = f_U*0.0 + np.nanmin(f_U)/5.0 # assuming 5-sigma
out_dict['FLUX_G'] = f_G
out_dict['FLUXERR_G'] = f_G*0.0 + np.nanmin(f_G)/5.0 # assuming 5-sigma
out_dict['FLUX_R'] = f_R
out_dict['FLUXERR_R'] = f_R*0.0 + np.nanmin(f_R)/5.0 # assuming 5-sigma
out_dict['FLUX_J'] = f_J
out_dict['FLUXERR_J'] = f_J*0.0 + np.nanmin(f_J)/5.0 # assuming 5-sigma
out_dict['FLUX_Ks'] = f_Ks
out_dict['FLUXERR_Ks'] = f_Ks*0.0 + np.nanmin(f_Ks)/5.0 # assuming 5-sigma

out_table = Table(out_dict)
out_table['z'].format = '%.4f'
out_table['RA'].format = '%.10f'
out_table['DEC'].format = '+%.9f'
for key in out_table.colnames:
    if key.startswith('FLUX'):
        out_table[key].format = '%.6e'
out_table.write('Erb_2006ApJ...646..107E_table1_photometry_converted_Jy.txt', format='ascii.fixed_width', delimiter='  ', bookend=True, overwrite=True)
with open('Erb_2006ApJ...646..107E_table1_photometry_converted_Jy.txt', 'r+') as fp:
    fp.seek(0)
    fp.write('#')
print('Output to "%s"'%('Erb_2006ApJ...646..107E_table1_photometry_converted_Jy.txt'))


