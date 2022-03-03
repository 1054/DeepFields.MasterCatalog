#!/bin/bash
# 
set -e

# downloaded from https://cesam.lam.fr/vvds/vvds_download.php
# uncompressed txt.gz
# edited txt files
# renamed column name "ID-IAU" as "ID_IAU"
# deleted first to second last commented header lines in the txt files so that topcat can recognize the columns
# note that the downloaded votable format *.xml.gz are problematic. do not use those.
# note that we have not used their spectral line measurements. we need more efforts to make the line flux table.

overwrite=1

#fields=(F02 F02 F10 F14 F22 CDFS)
#ftypes=(UDEEP DEEP WIDE WIDE WIDE DEEP)
if [[ ! -f "cesam_vvds_spCDFS_DEEP_Full_dzliu.fits" ]] || [[ $overwrite -gt 0 ]]; then
topcat -stilts tpipe \
        in="cesam_vvds_spCDFS_DEEP_Full.txt" \
        ifmt=ascii \
        cmd="addcol ID_SWIRE \"-99\"" \
        cmd="addcol ID_GALEX \"-99\"" \
        cmd="addcol FIELD \"\\\"CDFS\\\"\"" \
        cmd="addcol ZPHOT \"-99.9\"" \
        cmd="addcol STELLAR_MASS \"-99.9\"" \
        cmd="addcol SFR \"-99.9\"" \
        cmd="replacecol ID_SWIRE \"toLong(ID_SWIRE)\"" \
        cmd="replacecol ID_GALEX \"toLong(ID_GALEX)\"" \
        cmd="replacecol ZPHOT \"toDouble(ZPHOT)\"" \
        cmd="replacecol STELLAR_MASS \"toDouble(STELLAR_MASS)\"" \
        cmd="replacecol SFR \"toDouble(SFR)\"" \
        cmd="replacecol MAG_U_CFH12K  -name \"MAG_U_CFH12K\"    \"toDouble(MAG_U_CFH12K)\"" \
        cmd="replacecol MAGERR_AUTO_U -name \"MAGERR_U_CFH12K\" \"toDouble(MAGERR_AUTO_U)\"" \
        cmd="replacecol MAG_B_CFH12K  -name \"MAG_B_CFH12K\"    \"toDouble(MAG_B_CFH12K)\"" \
        cmd="replacecol MAGERR_AUTO_B -name \"MAGERR_B_CFH12K\" \"toDouble(MAGERR_AUTO_B)\"" \
        cmd="replacecol MAG_V_CFH12K  -name \"MAG_V_CFH12K\"    \"toDouble(MAG_V_CFH12K)\"" \
        cmd="replacecol MAGERR_AUTO_V -name \"MAGERR_V_CFH12K\" \"toDouble(MAGERR_AUTO_V)\"" \
        cmd="replacecol MAG_R_CFH12K  -name \"MAG_R_CFH12K\"    \"toDouble(MAG_R_CFH12K)\"" \
        cmd="replacecol MAGERR_AUTO_R -name \"MAGERR_R_CFH12K\" \"toDouble(MAGERR_AUTO_R)\"" \
        cmd="replacecol MAG_I_CFH12K  -name \"MAG_I_CFH12K\"    \"toDouble(MAG_I_CFH12K)\"" \
        cmd="replacecol MAGERR_AUTO_I -name \"MAGERR_I_CFH12K\" \"toDouble(MAGERR_AUTO_I)\"" \
        cmd="addcol                         \"MAG_U_CFHTLS\"    \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_U_CFHTLS\" \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAG_G_CFHTLS\"    \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_G_CFHTLS\" \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAG_R_CFHTLS\"    \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_R_CFHTLS\" \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAG_I_CFHTLS\"    \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_I_CFHTLS\" \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAG_Z_CFHTLS\"    \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_Z_CFHTLS\" \"toDouble(-99.9)\"" \
        cmd="replacecol MAGHST_B      -name \"MAG_B_HST\"       \"toDouble(MAGHST_B)\"" \
        cmd="replacecol MAGHSTERR_B   -name \"MAGERR_B_HST\"    \"toDouble(MAGHSTERR_B)\"" \
        cmd="replacecol MAGHST_V      -name \"MAG_V_HST\"       \"toDouble(MAGHST_V)\"" \
        cmd="replacecol MAGHSTERR_V   -name \"MAGERR_V_HST\"    \"toDouble(MAGHSTERR_V)\"" \
        cmd="replacecol MAGHST_I      -name \"MAG_I_HST\"       \"toDouble(MAGHST_I)\"" \
        cmd="replacecol MAGHSTERR_I   -name \"MAGERR_I_HST\"    \"toDouble(MAGHSTERR_I)\"" \
        cmd="replacecol MAGHST_Z      -name \"MAG_Z_HST\"       \"toDouble(MAGHST_Z)\"" \
        cmd="replacecol MAGHSTERR_Z   -name \"MAGERR_Z_HST\"    \"toDouble(MAGHSTERR_Z)\"" \
        cmd="addcol                         \"MAG_J_WIRDS\"     \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_J_WIRDS\"  \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAG_H_WIRDS\"     \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_H_WIRDS\"  \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAG_K_WIRDS\"     \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_K_WIRDS\"  \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAG_J_UKIDSS\"    \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_J_UKIDSS\" \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAG_K_UKIDSS\"    \"toDouble(-99.9)\"" \
        cmd="addcol                         \"MAGERR_K_UKIDSS\" \"toDouble(-99.9)\"" \
        cmd="keepcols \"NUM ID_IAU ID_SWIRE ID_GALEX ALPHA DELTA FIELD Z ZFLAGS ZPHOT STELLAR_MASS SFR MAG_U_CFH12K MAGERR_U_CFH12K MAG_B_CFH12K MAGERR_B_CFH12K MAG_V_CFH12K MAGERR_V_CFH12K MAG_R_CFH12K MAGERR_R_CFH12K MAG_I_CFH12K MAGERR_I_CFH12K MAG_B_HST MAGERR_B_HST MAG_V_HST MAGERR_V_HST MAG_I_HST MAGERR_I_HST MAG_Z_HST MAGERR_Z_HST MAG_U_CFHTLS MAGERR_U_CFHTLS MAG_G_CFHTLS MAGERR_G_CFHTLS MAG_R_CFHTLS MAGERR_R_CFHTLS MAG_I_CFHTLS MAGERR_I_CFHTLS MAG_Z_CFHTLS MAGERR_Z_CFHTLS MAG_J_WIRDS MAGERR_J_WIRDS MAG_H_WIRDS MAGERR_H_WIRDS MAG_K_WIRDS MAGERR_K_WIRDS MAG_J_UKIDSS MAGERR_J_UKIDSS MAG_K_UKIDSS MAGERR_K_UKIDSS\"" \
        out="cesam_vvds_spCDFS_DEEP_Full_dzliu.fits"
fi

if [[ ! -f "cesam_vvds_spF02_DEEP_Full_dzliu.fits" ]] || [[ $overwrite -gt 0 ]]; then
topcat -stilts tpipe \
        in="cesam_vvds_spF02_DEEP_Full.txt" \
        ifmt=ascii \
        cmd="addcol FIELD \"\\\"F0226-04\\\"\"" \
        cmd="replacecol ID_SWIRE \"toLong(ID_SWIRE)\"" \
        cmd="replacecol ID_GALEX \"toLong(ID_GALEX)\"" \
        cmd="replacecol ZPHOT \"toDouble(ZPHOT)\"" \
        cmd="replacecol STELLAR_MASS \"toDouble(STELLAR_MASS)\"" \
        cmd="replacecol SFR \"toDouble(SFR)\"" \
        cmd="replacecol \$8   -name \"MAG_U_CFH12K\"     \"toDouble(\$8)\"" \
        cmd="replacecol \$9   -name \"MAGERR_U_CFH12K\"  \"toDouble(\$9)\"" \
        cmd="replacecol \$10  -name \"MAG_B_CFH12K\"     \"toDouble(\$10)\"" \
        cmd="replacecol \$11  -name \"MAGERR_B_CFH12K\"  \"toDouble(\$11)\"" \
        cmd="replacecol \$12  -name \"MAG_V_CFH12K\"     \"toDouble(\$12)\"" \
        cmd="replacecol \$13  -name \"MAGERR_V_CFH12K\"  \"toDouble(\$13)\"" \
        cmd="replacecol \$14  -name \"MAG_R_CFH12K\"     \"toDouble(\$14)\"" \
        cmd="replacecol \$15  -name \"MAGERR_R_CFH12K\"  \"toDouble(\$15)\"" \
        cmd="replacecol \$16  -name \"MAG_I_CFH12K\"     \"toDouble(\$16)\"" \
        cmd="replacecol \$17  -name \"MAGERR_I_CFH12K\"  \"toDouble(\$17)\"" \
        cmd="replacecol \$18  -name \"MAG_U_CFHTLS\"     \"toDouble(\$18)\"" \
        cmd="replacecol \$19  -name \"MAGERR_U_CFHTLS\"  \"toDouble(\$19)\"" \
        cmd="replacecol \$20  -name \"MAG_G_CFHTLS\"     \"toDouble(\$20)\"" \
        cmd="replacecol \$21  -name \"MAGERR_G_CFHTLS\"  \"toDouble(\$21)\"" \
        cmd="replacecol \$22  -name \"MAG_R_CFHTLS\"     \"toDouble(\$22)\"" \
        cmd="replacecol \$23  -name \"MAGERR_R_CFHTLS\"  \"toDouble(\$23)\"" \
        cmd="replacecol \$24  -name \"MAG_I_CFHTLS\"     \"toDouble(\$24)\"" \
        cmd="replacecol \$25  -name \"MAGERR_I_CFHTLS\"  \"toDouble(\$25)\"" \
        cmd="replacecol \$26  -name \"MAG_Z_CFHTLS\"     \"toDouble(\$26)\"" \
        cmd="replacecol \$27  -name \"MAGERR_Z_CFHTLS\"  \"toDouble(\$27)\"" \
        cmd="addcol                 \"MAG_B_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_B_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_V_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_V_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_I_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_I_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_Z_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_Z_HST\"     \"toDouble(-99.9)\"" \
        cmd="replacecol \$110 -name \"MAG_J_WIRDS\"      \"toDouble(\$110)\"" \
        cmd="replacecol \$111 -name \"MAGERR_J_WIRDS\"   \"toDouble(\$111)\"" \
        cmd="replacecol \$112 -name \"MAG_H_WIRDS\"      \"toDouble(\$112)\"" \
        cmd="replacecol \$113 -name \"MAGERR_H_WIRDS\"   \"toDouble(\$113)\"" \
        cmd="replacecol \$114 -name \"MAG_K_WIRDS\"      \"toDouble(\$114)\"" \
        cmd="replacecol \$115 -name \"MAGERR_K_WIRDS\"   \"toDouble(\$115)\"" \
        cmd="replacecol \$122 -name \"MAG_J_UKIDSS\"     \"toDouble(\$122)\"" \
        cmd="replacecol \$123 -name \"MAGERR_J_UKIDSS\"  \"toDouble(\$123)\"" \
        cmd="replacecol \$125 -name \"MAG_K_UKIDSS\"     \"toDouble(\$125)\"" \
        cmd="replacecol \$126 -name \"MAGERR_K_UKIDSS\"  \"toDouble(\$126)\"" \
        cmd="keepcols \"NUM ID_IAU ID_SWIRE ID_GALEX ALPHA DELTA FIELD Z ZFLAGS ZPHOT STELLAR_MASS SFR MAG_U_CFH12K MAGERR_U_CFH12K MAG_B_CFH12K MAGERR_B_CFH12K MAG_V_CFH12K MAGERR_V_CFH12K MAG_R_CFH12K MAGERR_R_CFH12K MAG_I_CFH12K MAGERR_I_CFH12K MAG_B_HST MAGERR_B_HST MAG_V_HST MAGERR_V_HST MAG_I_HST MAGERR_I_HST MAG_Z_HST MAGERR_Z_HST MAG_U_CFHTLS MAGERR_U_CFHTLS MAG_G_CFHTLS MAGERR_G_CFHTLS MAG_R_CFHTLS MAGERR_R_CFHTLS MAG_I_CFHTLS MAGERR_I_CFHTLS MAG_Z_CFHTLS MAGERR_Z_CFHTLS MAG_J_WIRDS MAGERR_J_WIRDS MAG_H_WIRDS MAGERR_H_WIRDS MAG_K_WIRDS MAGERR_K_WIRDS MAG_J_UKIDSS MAGERR_J_UKIDSS MAG_K_UKIDSS MAGERR_K_UKIDSS\"" \
        out="cesam_vvds_spF02_DEEP_Full_dzliu.fits"
fi

if [[ ! -f "cesam_vvds_spF02_UDEEP_Full_dzliu.fits" ]] || [[ $overwrite -gt 0 ]]; then
topcat -stilts tpipe \
        in="cesam_vvds_spF02_UDEEP_Full.txt" \
        ifmt=ascii \
        cmd="addcol FIELD \"\\\"F0226-04\\\"\"" \
        cmd="replacecol ID_SWIRE \"toLong(ID_SWIRE)\"" \
        cmd="replacecol ID_GALEX \"toLong(ID_GALEX)\"" \
        cmd="replacecol ZPHOT \"toDouble(ZPHOT)\"" \
        cmd="replacecol STELLAR_MASS \"toDouble(STELLAR_MASS)\"" \
        cmd="replacecol SFR \"toDouble(SFR)\"" \
        cmd="replacecol \$8   -name \"MAG_U_CFH12K\"     \"toDouble(\$8)\"" \
        cmd="replacecol \$9   -name \"MAGERR_U_CFH12K\"  \"toDouble(\$9)\"" \
        cmd="replacecol \$10  -name \"MAG_B_CFH12K\"     \"toDouble(\$10)\"" \
        cmd="replacecol \$11  -name \"MAGERR_B_CFH12K\"  \"toDouble(\$11)\"" \
        cmd="replacecol \$12  -name \"MAG_V_CFH12K\"     \"toDouble(\$12)\"" \
        cmd="replacecol \$13  -name \"MAGERR_V_CFH12K\"  \"toDouble(\$13)\"" \
        cmd="replacecol \$14  -name \"MAG_R_CFH12K\"     \"toDouble(\$14)\"" \
        cmd="replacecol \$15  -name \"MAGERR_R_CFH12K\"  \"toDouble(\$15)\"" \
        cmd="replacecol \$16  -name \"MAG_I_CFH12K\"     \"toDouble(\$16)\"" \
        cmd="replacecol \$17  -name \"MAGERR_I_CFH12K\"  \"toDouble(\$17)\"" \
        cmd="replacecol \$18  -name \"MAG_U_CFHTLS\"     \"toDouble(\$18)\"" \
        cmd="replacecol \$19  -name \"MAGERR_U_CFHTLS\"  \"toDouble(\$19)\"" \
        cmd="replacecol \$20  -name \"MAG_G_CFHTLS\"     \"toDouble(\$20)\"" \
        cmd="replacecol \$21  -name \"MAGERR_G_CFHTLS\"  \"toDouble(\$21)\"" \
        cmd="replacecol \$22  -name \"MAG_R_CFHTLS\"     \"toDouble(\$22)\"" \
        cmd="replacecol \$23  -name \"MAGERR_R_CFHTLS\"  \"toDouble(\$23)\"" \
        cmd="replacecol \$24  -name \"MAG_I_CFHTLS\"     \"toDouble(\$24)\"" \
        cmd="replacecol \$25  -name \"MAGERR_I_CFHTLS\"  \"toDouble(\$25)\"" \
        cmd="replacecol \$26  -name \"MAG_Z_CFHTLS\"     \"toDouble(\$26)\"" \
        cmd="replacecol \$27  -name \"MAGERR_Z_CFHTLS\"  \"toDouble(\$27)\"" \
        cmd="addcol                 \"MAG_B_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_B_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_V_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_V_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_I_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_I_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_Z_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_Z_HST\"     \"toDouble(-99.9)\"" \
        cmd="replacecol \$105 -name \"MAG_J_WIRDS\"      \"toDouble(\$105)\"" \
        cmd="replacecol \$106 -name \"MAGERR_J_WIRDS\"   \"toDouble(\$106)\"" \
        cmd="replacecol \$107 -name \"MAG_H_WIRDS\"      \"toDouble(\$107)\"" \
        cmd="replacecol \$108 -name \"MAGERR_H_WIRDS\"   \"toDouble(\$108)\"" \
        cmd="replacecol \$109 -name \"MAG_K_WIRDS\"      \"toDouble(\$109)\"" \
        cmd="replacecol \$110 -name \"MAGERR_K_WIRDS\"   \"toDouble(\$110)\"" \
        cmd="replacecol \$117 -name \"MAG_J_UKIDSS\"     \"toDouble(\$117)\"" \
        cmd="replacecol \$118 -name \"MAGERR_J_UKIDSS\"  \"toDouble(\$118)\"" \
        cmd="replacecol \$120 -name \"MAG_K_UKIDSS\"     \"toDouble(\$120)\"" \
        cmd="replacecol \$121 -name \"MAGERR_K_UKIDSS\"  \"toDouble(\$121)\"" \
        cmd="keepcols \"NUM ID_IAU ID_SWIRE ID_GALEX ALPHA DELTA FIELD Z ZFLAGS ZPHOT STELLAR_MASS SFR MAG_U_CFH12K MAGERR_U_CFH12K MAG_B_CFH12K MAGERR_B_CFH12K MAG_V_CFH12K MAGERR_V_CFH12K MAG_R_CFH12K MAGERR_R_CFH12K MAG_I_CFH12K MAGERR_I_CFH12K MAG_B_HST MAGERR_B_HST MAG_V_HST MAGERR_V_HST MAG_I_HST MAGERR_I_HST MAG_Z_HST MAGERR_Z_HST MAG_U_CFHTLS MAGERR_U_CFHTLS MAG_G_CFHTLS MAGERR_G_CFHTLS MAG_R_CFHTLS MAGERR_R_CFHTLS MAG_I_CFHTLS MAGERR_I_CFHTLS MAG_Z_CFHTLS MAGERR_Z_CFHTLS MAG_J_WIRDS MAGERR_J_WIRDS MAG_H_WIRDS MAGERR_H_WIRDS MAG_K_WIRDS MAGERR_K_WIRDS MAG_J_UKIDSS MAGERR_J_UKIDSS MAG_K_UKIDSS MAGERR_K_UKIDSS\"" \
        out="cesam_vvds_spF02_UDEEP_Full_dzliu.fits"
        # 
        # note that MAG_I_CFH12K and MAGERR_I_CFH12K should actually be MAG_I_CFHTLS_T0003 and MAGERR_AUTO_I_t0003
        # 
        # checkd that F02_UDEEP has no overlap source within 0.5 arcsec with F02_DEEP, only two sources matched within 1 arcsec, one has sep 0.5 arcsec, the other 0.9 arcsec.
        # 
fi

if [[ ! -f "cesam_vvds_spF10_WIDE_Full_dzliu.fits" ]] || [[ $overwrite -gt 0 ]]; then
topcat -stilts tpipe \
        in="cesam_vvds_spF10_WIDE_Full.txt" \
        ifmt=ascii \
        cmd="addcol ID_SWIRE \"-99\"" \
        cmd="addcol ID_GALEX \"-99\"" \
        cmd="addcol FIELD \"\\\"F1003+01\\\"\"" \
        cmd="addcol ZPHOT \"-99.9\"" \
        cmd="addcol STELLAR_MASS \"-99.9\"" \
        cmd="addcol SFR \"-99.9\"" \
        cmd="replacecol ID_SWIRE \"toLong(ID_SWIRE)\"" \
        cmd="replacecol ID_GALEX \"toLong(ID_GALEX)\"" \
        cmd="replacecol ZPHOT \"toDouble(ZPHOT)\"" \
        cmd="replacecol STELLAR_MASS \"toDouble(STELLAR_MASS)\"" \
        cmd="replacecol SFR \"toDouble(SFR)\"" \
        cmd="replacecol \$8   -name \"MAG_U_CFH12K\"     \"toDouble(\$8)\"" \
        cmd="replacecol \$9   -name \"MAGERR_U_CFH12K\"  \"toDouble(\$9)\"" \
        cmd="replacecol \$10  -name \"MAG_B_CFH12K\"     \"toDouble(\$10)\"" \
        cmd="replacecol \$11  -name \"MAGERR_B_CFH12K\"  \"toDouble(\$11)\"" \
        cmd="replacecol \$12  -name \"MAG_V_CFH12K\"     \"toDouble(\$12)\"" \
        cmd="replacecol \$13  -name \"MAGERR_V_CFH12K\"  \"toDouble(\$13)\"" \
        cmd="replacecol \$14  -name \"MAG_R_CFH12K\"     \"toDouble(\$14)\"" \
        cmd="replacecol \$15  -name \"MAGERR_R_CFH12K\"  \"toDouble(\$15)\"" \
        cmd="replacecol \$16  -name \"MAG_I_CFH12K\"     \"toDouble(\$16)\"" \
        cmd="replacecol \$17  -name \"MAGERR_I_CFH12K\"  \"toDouble(\$17)\"" \
        cmd="replacecol \$95  -name \"MAG_U_CFHTLS\"     \"toDouble(\$95)\"" \
        cmd="replacecol \$96  -name \"MAGERR_U_CFHTLS\"  \"toDouble(\$96)\"" \
        cmd="replacecol \$97  -name \"MAG_G_CFHTLS\"     \"toDouble(\$97)\"" \
        cmd="replacecol \$98  -name \"MAGERR_G_CFHTLS\"  \"toDouble(\$98)\"" \
        cmd="replacecol \$99  -name \"MAG_R_CFHTLS\"     \"toDouble(\$99)\"" \
        cmd="replacecol \$100 -name \"MAGERR_R_CFHTLS\"  \"toDouble(\$100)\"" \
        cmd="replacecol \$101 -name \"MAG_I_CFHTLS\"     \"toDouble(\$101)\"" \
        cmd="replacecol \$102 -name \"MAGERR_I_CFHTLS\"  \"toDouble(\$102)\"" \
        cmd="replacecol \$103 -name \"MAG_Z_CFHTLS\"     \"toDouble(\$103)\"" \
        cmd="replacecol \$104 -name \"MAGERR_Z_CFHTLS\"  \"toDouble(\$104)\"" \
        cmd="addcol                 \"MAG_B_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_B_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_V_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_V_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_I_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_I_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_Z_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_Z_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_J_WIRDS\"      \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_J_WIRDS\"   \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_H_WIRDS\"      \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_H_WIRDS\"   \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_K_WIRDS\"      \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_K_WIRDS\"   \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_J_UKIDSS\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_J_UKIDSS\"  \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_K_UKIDSS\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_K_UKIDSS\"  \"toDouble(-99.9)\"" \
        cmd="keepcols \"NUM ID_IAU ID_SWIRE ID_GALEX ALPHA DELTA FIELD Z ZFLAGS ZPHOT STELLAR_MASS SFR MAG_U_CFH12K MAGERR_U_CFH12K MAG_B_CFH12K MAGERR_B_CFH12K MAG_V_CFH12K MAGERR_V_CFH12K MAG_R_CFH12K MAGERR_R_CFH12K MAG_I_CFH12K MAGERR_I_CFH12K MAG_B_HST MAGERR_B_HST MAG_V_HST MAGERR_V_HST MAG_I_HST MAGERR_I_HST MAG_Z_HST MAGERR_Z_HST MAG_U_CFHTLS MAGERR_U_CFHTLS MAG_G_CFHTLS MAGERR_G_CFHTLS MAG_R_CFHTLS MAGERR_R_CFHTLS MAG_I_CFHTLS MAGERR_I_CFHTLS MAG_Z_CFHTLS MAGERR_Z_CFHTLS MAG_J_WIRDS MAGERR_J_WIRDS MAG_H_WIRDS MAGERR_H_WIRDS MAG_K_WIRDS MAGERR_K_WIRDS MAG_J_UKIDSS MAGERR_J_UKIDSS MAG_K_UKIDSS MAGERR_K_UKIDSS\"" \
        out="cesam_vvds_spF10_WIDE_Full_dzliu.fits"
fi

if [[ ! -f "cesam_vvds_spF14_WIDE_Full_dzliu.fits" ]] || [[ $overwrite -gt 0 ]]; then
topcat -stilts tpipe \
        in="cesam_vvds_spF14_WIDE_Full.txt" \
        ifmt=ascii \
        cmd="addcol ID_SWIRE \"-99\"" \
        cmd="addcol ID_GALEX \"-99\"" \
        cmd="addcol FIELD \"\\\"F1400+05\\\"\"" \
        cmd="addcol ZPHOT \"-99.9\"" \
        cmd="addcol STELLAR_MASS \"-99.9\"" \
        cmd="addcol SFR \"-99.9\"" \
        cmd="replacecol ID_SWIRE \"toLong(ID_SWIRE)\"" \
        cmd="replacecol ID_GALEX \"toLong(ID_GALEX)\"" \
        cmd="replacecol ZPHOT \"toDouble(ZPHOT)\"" \
        cmd="replacecol STELLAR_MASS \"toDouble(STELLAR_MASS)\"" \
        cmd="replacecol SFR \"toDouble(SFR)\"" \
        cmd="replacecol \$8   -name \"MAG_U_CFH12K\"     \"toDouble(\$8)\"" \
        cmd="replacecol \$9   -name \"MAGERR_U_CFH12K\"  \"toDouble(\$9)\"" \
        cmd="replacecol \$10  -name \"MAG_B_CFH12K\"     \"toDouble(\$10)\"" \
        cmd="replacecol \$11  -name \"MAGERR_B_CFH12K\"  \"toDouble(\$11)\"" \
        cmd="replacecol \$12  -name \"MAG_V_CFH12K\"     \"toDouble(\$12)\"" \
        cmd="replacecol \$13  -name \"MAGERR_V_CFH12K\"  \"toDouble(\$13)\"" \
        cmd="replacecol \$14  -name \"MAG_R_CFH12K\"     \"toDouble(\$14)\"" \
        cmd="replacecol \$15  -name \"MAGERR_R_CFH12K\"  \"toDouble(\$15)\"" \
        cmd="replacecol \$16  -name \"MAG_I_CFH12K\"     \"toDouble(\$16)\"" \
        cmd="replacecol \$17  -name \"MAGERR_I_CFH12K\"  \"toDouble(\$17)\"" \
        cmd="replacecol \$95  -name \"MAG_U_CFHTLS\"     \"toDouble(\$95)\"" \
        cmd="replacecol \$96  -name \"MAGERR_U_CFHTLS\"  \"toDouble(\$96)\"" \
        cmd="replacecol \$97  -name \"MAG_G_CFHTLS\"     \"toDouble(\$97)\"" \
        cmd="replacecol \$98  -name \"MAGERR_G_CFHTLS\"  \"toDouble(\$98)\"" \
        cmd="replacecol \$99  -name \"MAG_R_CFHTLS\"     \"toDouble(\$99)\"" \
        cmd="replacecol \$100 -name \"MAGERR_R_CFHTLS\"  \"toDouble(\$100)\"" \
        cmd="replacecol \$101 -name \"MAG_I_CFHTLS\"     \"toDouble(\$101)\"" \
        cmd="replacecol \$102 -name \"MAGERR_I_CFHTLS\"  \"toDouble(\$102)\"" \
        cmd="replacecol \$103 -name \"MAG_Z_CFHTLS\"     \"toDouble(\$103)\"" \
        cmd="replacecol \$104 -name \"MAGERR_Z_CFHTLS\"  \"toDouble(\$104)\"" \
        cmd="addcol                 \"MAG_B_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_B_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_V_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_V_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_I_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_I_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_Z_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_Z_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_J_WIRDS\"      \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_J_WIRDS\"   \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_H_WIRDS\"      \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_H_WIRDS\"   \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_K_WIRDS\"      \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_K_WIRDS\"   \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_J_UKIDSS\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_J_UKIDSS\"  \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_K_UKIDSS\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_K_UKIDSS\"  \"toDouble(-99.9)\"" \
        cmd="keepcols \"NUM ID_IAU ID_SWIRE ID_GALEX ALPHA DELTA FIELD Z ZFLAGS ZPHOT STELLAR_MASS SFR MAG_U_CFH12K MAGERR_U_CFH12K MAG_B_CFH12K MAGERR_B_CFH12K MAG_V_CFH12K MAGERR_V_CFH12K MAG_R_CFH12K MAGERR_R_CFH12K MAG_I_CFH12K MAGERR_I_CFH12K MAG_B_HST MAGERR_B_HST MAG_V_HST MAGERR_V_HST MAG_I_HST MAGERR_I_HST MAG_Z_HST MAGERR_Z_HST MAG_U_CFHTLS MAGERR_U_CFHTLS MAG_G_CFHTLS MAGERR_G_CFHTLS MAG_R_CFHTLS MAGERR_R_CFHTLS MAG_I_CFHTLS MAGERR_I_CFHTLS MAG_Z_CFHTLS MAGERR_Z_CFHTLS MAG_J_WIRDS MAGERR_J_WIRDS MAG_H_WIRDS MAGERR_H_WIRDS MAG_K_WIRDS MAGERR_K_WIRDS MAG_J_UKIDSS MAGERR_J_UKIDSS MAG_K_UKIDSS MAGERR_K_UKIDSS\"" \
        out="cesam_vvds_spF14_WIDE_Full_dzliu.fits"
fi

if [[ ! -f "cesam_vvds_spF22_WIDE_Full_dzliu.fits" ]] || [[ $overwrite -gt 0 ]]; then
topcat -stilts tpipe \
        in="cesam_vvds_spF22_WIDE_Full.txt" \
        ifmt=ascii \
        cmd="addcol ID_SWIRE \"-99\"" \
        cmd="addcol ID_GALEX \"-99\"" \
        cmd="addcol FIELD \"\\\"F2217+00\\\"\"" \
        cmd="replacecol ID_SWIRE \"toLong(ID_SWIRE)\"" \
        cmd="replacecol ID_GALEX \"toLong(ID_GALEX)\"" \
        cmd="replacecol ZPHOT \"toDouble(ZPHOT)\"" \
        cmd="replacecol STELLAR_MASS \"toDouble(STELLAR_MASS)\"" \
        cmd="replacecol SFR \"toDouble(SFR)\"" \
        cmd="replacecol \$8   -name \"MAG_U_CFH12K\"     \"toDouble(\$8)\"" \
        cmd="replacecol \$9   -name \"MAGERR_U_CFH12K\"  \"toDouble(\$9)\"" \
        cmd="replacecol \$10  -name \"MAG_B_CFH12K\"     \"toDouble(\$10)\"" \
        cmd="replacecol \$11  -name \"MAGERR_B_CFH12K\"  \"toDouble(\$11)\"" \
        cmd="replacecol \$12  -name \"MAG_V_CFH12K\"     \"toDouble(\$12)\"" \
        cmd="replacecol \$13  -name \"MAGERR_V_CFH12K\"  \"toDouble(\$13)\"" \
        cmd="replacecol \$14  -name \"MAG_R_CFH12K\"     \"toDouble(\$14)\"" \
        cmd="replacecol \$15  -name \"MAGERR_R_CFH12K\"  \"toDouble(\$15)\"" \
        cmd="replacecol \$16  -name \"MAG_I_CFH12K\"     \"toDouble(\$16)\"" \
        cmd="replacecol \$17  -name \"MAGERR_I_CFH12K\"  \"toDouble(\$17)\"" \
        cmd="replacecol \$18  -name \"MAG_U_CFHTLS\"     \"toDouble(\$18)\"" \
        cmd="replacecol \$19  -name \"MAGERR_U_CFHTLS\"  \"toDouble(\$19)\"" \
        cmd="replacecol \$20  -name \"MAG_G_CFHTLS\"     \"toDouble(\$20)\"" \
        cmd="replacecol \$21  -name \"MAGERR_G_CFHTLS\"  \"toDouble(\$21)\"" \
        cmd="replacecol \$22  -name \"MAG_R_CFHTLS\"     \"toDouble(\$22)\"" \
        cmd="replacecol \$23  -name \"MAGERR_R_CFHTLS\"  \"toDouble(\$23)\"" \
        cmd="replacecol \$24  -name \"MAG_I_CFHTLS\"     \"toDouble(\$24)\"" \
        cmd="replacecol \$25  -name \"MAGERR_I_CFHTLS\"  \"toDouble(\$25)\"" \
        cmd="replacecol \$26  -name \"MAG_Z_CFHTLS\"     \"toDouble(\$26)\"" \
        cmd="replacecol \$27  -name \"MAGERR_Z_CFHTLS\"  \"toDouble(\$27)\"" \
        cmd="addcol                 \"MAG_B_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_B_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_V_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_V_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_I_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_I_HST\"     \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAG_Z_HST\"        \"toDouble(-99.9)\"" \
        cmd="addcol                 \"MAGERR_Z_HST\"     \"toDouble(-99.9)\"" \
        cmd="replacecol \$105 -name \"MAG_J_WIRDS\"      \"toDouble(\$105)\"" \
        cmd="replacecol \$106 -name \"MAGERR_J_WIRDS\"   \"toDouble(\$106)\"" \
        cmd="replacecol \$107 -name \"MAG_H_WIRDS\"      \"toDouble(\$107)\"" \
        cmd="replacecol \$108 -name \"MAGERR_H_WIRDS\"   \"toDouble(\$108)\"" \
        cmd="replacecol \$109 -name \"MAG_K_WIRDS\"      \"toDouble(\$109)\"" \
        cmd="replacecol \$110 -name \"MAGERR_K_WIRDS\"   \"toDouble(\$110)\"" \
        cmd="replacecol \$117 -name \"MAG_J_UKIDSS\"     \"toDouble(\$117)\"" \
        cmd="replacecol \$118 -name \"MAGERR_J_UKIDSS\"  \"toDouble(\$118)\"" \
        cmd="replacecol \$120 -name \"MAG_K_UKIDSS\"     \"toDouble(\$120)\"" \
        cmd="replacecol \$121 -name \"MAGERR_K_UKIDSS\"  \"toDouble(\$121)\"" \
        cmd="keepcols \"NUM ID_IAU ID_SWIRE ID_GALEX ALPHA DELTA FIELD Z ZFLAGS ZPHOT STELLAR_MASS SFR MAG_U_CFH12K MAGERR_U_CFH12K MAG_B_CFH12K MAGERR_B_CFH12K MAG_V_CFH12K MAGERR_V_CFH12K MAG_R_CFH12K MAGERR_R_CFH12K MAG_I_CFH12K MAGERR_I_CFH12K MAG_B_HST MAGERR_B_HST MAG_V_HST MAGERR_V_HST MAG_I_HST MAGERR_I_HST MAG_Z_HST MAGERR_Z_HST MAG_U_CFHTLS MAGERR_U_CFHTLS MAG_G_CFHTLS MAGERR_G_CFHTLS MAG_R_CFHTLS MAGERR_R_CFHTLS MAG_I_CFHTLS MAGERR_I_CFHTLS MAG_Z_CFHTLS MAGERR_Z_CFHTLS MAG_J_WIRDS MAGERR_J_WIRDS MAG_H_WIRDS MAGERR_H_WIRDS MAG_K_WIRDS MAGERR_K_WIRDS MAG_J_UKIDSS MAGERR_J_UKIDSS MAG_K_UKIDSS MAGERR_K_UKIDSS\"" \
        out="cesam_vvds_spF22_WIDE_Full_dzliu.fits"
fi
        
topcat -stilts tcatn nin=6 \
        in1="cesam_vvds_spCDFS_DEEP_Full_dzliu.fits" \
        in2="cesam_vvds_spF02_DEEP_Full_dzliu.fits" \
        in3="cesam_vvds_spF02_UDEEP_Full_dzliu.fits" \
        in4="cesam_vvds_spF10_WIDE_Full_dzliu.fits" \
        in5="cesam_vvds_spF14_WIDE_Full_dzliu.fits" \
        in6="cesam_vvds_spF22_WIDE_Full_dzliu.fits" \
        ocmd="replacecol ID_SWIRE \"ID_SWIRE==9999999? -99 : ID_SWIRE\"" \
        ocmd="replacecol Z \"Z>=9.9? -99.9 : Z\"" \
        ocmd="replacecol MAGERR_U_CFH12K \"MAGERR_U_CFH12K>=0.0 && MAGERR_U_CFH12K<=0.01 ? 0.01 : MAGERR_U_CFH12K\"" \
        ocmd="replacecol MAGERR_B_CFH12K \"MAGERR_B_CFH12K>=0.0 && MAGERR_B_CFH12K<=0.01 ? 0.01 : MAGERR_B_CFH12K\"" \
        ocmd="replacecol MAGERR_V_CFH12K \"MAGERR_V_CFH12K>=0.0 && MAGERR_V_CFH12K<=0.01 ? 0.01 : MAGERR_V_CFH12K\"" \
        ocmd="replacecol MAGERR_R_CFH12K \"MAGERR_R_CFH12K>=0.0 && MAGERR_R_CFH12K<=0.01 ? 0.01 : MAGERR_R_CFH12K\"" \
        ocmd="replacecol MAGERR_I_CFH12K \"MAGERR_I_CFH12K>=0.0 && MAGERR_I_CFH12K<=0.01 ? 0.01 : MAGERR_I_CFH12K\"" \
        ocmd="replacecol MAGERR_B_HST    \"MAGERR_B_HST>=0.0 && MAGERR_B_HST<=0.01 ? 0.01 : MAGERR_B_HST\"" \
        ocmd="replacecol MAGERR_V_HST    \"MAGERR_V_HST>=0.0 && MAGERR_V_HST<=0.01 ? 0.01 : MAGERR_V_HST\"" \
        ocmd="replacecol MAGERR_I_HST    \"MAGERR_I_HST>=0.0 && MAGERR_I_HST<=0.01 ? 0.01 : MAGERR_I_HST\"" \
        ocmd="replacecol MAGERR_Z_HST    \"MAGERR_Z_HST>=0.0 && MAGERR_Z_HST<=0.01 ? 0.01 : MAGERR_Z_HST\"" \
        ocmd="replacecol MAGERR_U_CFHTLS \"MAGERR_U_CFHTLS>=0.0 && MAGERR_U_CFHTLS<=0.01 ? 0.01 : MAGERR_U_CFHTLS\"" \
        ocmd="replacecol MAGERR_G_CFHTLS \"MAGERR_G_CFHTLS>=0.0 && MAGERR_G_CFHTLS<=0.01 ? 0.01 : MAGERR_G_CFHTLS\"" \
        ocmd="replacecol MAGERR_R_CFHTLS \"MAGERR_R_CFHTLS>=0.0 && MAGERR_R_CFHTLS<=0.01 ? 0.01 : MAGERR_R_CFHTLS\"" \
        ocmd="replacecol MAGERR_I_CFHTLS \"MAGERR_I_CFHTLS>=0.0 && MAGERR_I_CFHTLS<=0.01 ? 0.01 : MAGERR_I_CFHTLS\"" \
        ocmd="replacecol MAGERR_Z_CFHTLS \"MAGERR_Z_CFHTLS>=0.0 && MAGERR_Z_CFHTLS<=0.01 ? 0.01 : MAGERR_Z_CFHTLS\"" \
        ocmd="replacecol MAGERR_J_WIRDS  \"MAGERR_J_WIRDS>=0.0 && MAGERR_J_WIRDS<=0.01 ? 0.01 : MAGERR_J_WIRDS\"" \
        ocmd="replacecol MAGERR_H_WIRDS  \"MAGERR_H_WIRDS>=0.0 && MAGERR_H_WIRDS<=0.01 ? 0.01 : MAGERR_H_WIRDS\"" \
        ocmd="replacecol MAGERR_K_WIRDS  \"MAGERR_K_WIRDS>=0.0 && MAGERR_K_WIRDS<=0.01 ? 0.01 : MAGERR_K_WIRDS\"" \
        ocmd="replacecol MAGERR_J_UKIDSS \"MAGERR_J_UKIDSS>=0.0 && MAGERR_J_UKIDSS<=0.01 ? 0.01 : MAGERR_J_UKIDSS\"" \
        ocmd="replacecol MAGERR_K_UKIDSS \"MAGERR_K_UKIDSS>=0.0 && MAGERR_K_UKIDSS<=0.01 ? 0.01 : MAGERR_K_UKIDSS\"" \
        ocmd="addcol FLUX_U_CFH12K     -units \"Jy\" \"MAG_U_CFH12K>0.0 && MAG_U_CFH12K<90.0 ? 3631.0 * pow(10, MAG_U_CFH12K/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_U_CFH12K  -units \"Jy\" \"MAG_U_CFH12K>0.0 && MAG_U_CFH12K<90.0 ? MAGERR_U_CFH12K * FLUX_U_CFH12K / 1.086 : NULL\"" \
        ocmd="addcol FLUX_B_CFH12K     -units \"Jy\" \"MAG_B_CFH12K>0.0 && MAG_B_CFH12K<90.0 ? 3631.0 * pow(10, MAG_B_CFH12K/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_B_CFH12K  -units \"Jy\" \"MAG_B_CFH12K>0.0 && MAG_B_CFH12K<90.0 ? MAGERR_B_CFH12K * FLUX_B_CFH12K / 1.086 : NULL\"" \
        ocmd="addcol FLUX_V_CFH12K     -units \"Jy\" \"MAG_V_CFH12K>0.0 && MAG_V_CFH12K<90.0 ? 3631.0 * pow(10, MAG_V_CFH12K/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_V_CFH12K  -units \"Jy\" \"MAG_V_CFH12K>0.0 && MAG_V_CFH12K<90.0 ? MAGERR_V_CFH12K * FLUX_V_CFH12K / 1.086 : NULL\"" \
        ocmd="addcol FLUX_R_CFH12K     -units \"Jy\" \"MAG_R_CFH12K>0.0 && MAG_R_CFH12K<90.0 ? 3631.0 * pow(10, MAG_R_CFH12K/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_R_CFH12K  -units \"Jy\" \"MAG_R_CFH12K>0.0 && MAG_R_CFH12K<90.0 ? MAGERR_R_CFH12K * FLUX_R_CFH12K / 1.086 : NULL\"" \
        ocmd="addcol FLUX_I_CFH12K     -units \"Jy\" \"MAG_I_CFH12K>0.0 && MAG_I_CFH12K<90.0 ? 3631.0 * pow(10, MAG_I_CFH12K/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_I_CFH12K  -units \"Jy\" \"MAG_I_CFH12K>0.0 && MAG_I_CFH12K<90.0 ? MAGERR_I_CFH12K * FLUX_I_CFH12K / 1.086 : NULL\"" \
        ocmd="addcol FLUX_B_HST        -units \"Jy\" \"MAG_B_HST>0.0    && MAG_B_HST<90.0    ? 3631.0 * pow(10, MAG_B_HST/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_B_HST     -units \"Jy\" \"MAG_B_HST>0.0    && MAG_B_HST<90.0    ? MAGERR_B_HST * FLUX_B_HST / 1.086 : NULL\"" \
        ocmd="addcol FLUX_V_HST        -units \"Jy\" \"MAG_V_HST>0.0    && MAG_V_HST<90.0    ? 3631.0 * pow(10, MAG_V_HST/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_V_HST     -units \"Jy\" \"MAG_V_HST>0.0    && MAG_V_HST<90.0    ? MAGERR_V_HST * FLUX_V_HST / 1.086 : NULL\"" \
        ocmd="addcol FLUX_I_HST        -units \"Jy\" \"MAG_I_HST>0.0    && MAG_I_HST<90.0    ? 3631.0 * pow(10, MAG_I_HST/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_I_HST     -units \"Jy\" \"MAG_I_HST>0.0    && MAG_I_HST<90.0    ? MAGERR_I_HST * FLUX_I_HST / 1.086 : NULL\"" \
        ocmd="addcol FLUX_Z_HST        -units \"Jy\" \"MAG_Z_HST>0.0    && MAG_Z_HST<90.0    ? 3631.0 * pow(10, MAG_Z_HST/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_Z_HST     -units \"Jy\" \"MAG_Z_HST>0.0    && MAG_Z_HST<90.0    ? MAGERR_Z_HST * FLUX_Z_HST / 1.086 : NULL\"" \
        ocmd="addcol FLUX_U_CFHTLS     -units \"Jy\" \"MAG_U_CFHTLS>0.0 && MAG_U_CFHTLS<90.0 ? 3631.0 * pow(10, MAG_U_CFHTLS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_U_CFHTLS  -units \"Jy\" \"MAG_U_CFHTLS>0.0 && MAG_U_CFHTLS<90.0 ? MAGERR_U_CFHTLS * FLUX_U_CFHTLS / 1.086 : NULL\"" \
        ocmd="addcol FLUX_G_CFHTLS     -units \"Jy\" \"MAG_G_CFHTLS>0.0 && MAG_G_CFHTLS<90.0 ? 3631.0 * pow(10, MAG_G_CFHTLS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_G_CFHTLS  -units \"Jy\" \"MAG_G_CFHTLS>0.0 && MAG_G_CFHTLS<90.0 ? MAGERR_G_CFHTLS * FLUX_G_CFHTLS / 1.086 : NULL\"" \
        ocmd="addcol FLUX_R_CFHTLS     -units \"Jy\" \"MAG_R_CFHTLS>0.0 && MAG_R_CFHTLS<90.0 ? 3631.0 * pow(10, MAG_R_CFHTLS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_R_CFHTLS  -units \"Jy\" \"MAG_R_CFHTLS>0.0 && MAG_R_CFHTLS<90.0 ? MAGERR_R_CFHTLS * FLUX_R_CFHTLS / 1.086 : NULL\"" \
        ocmd="addcol FLUX_I_CFHTLS     -units \"Jy\" \"MAG_I_CFHTLS>0.0 && MAG_I_CFHTLS<90.0 ? 3631.0 * pow(10, MAG_I_CFHTLS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_I_CFHTLS  -units \"Jy\" \"MAG_I_CFHTLS>0.0 && MAG_I_CFHTLS<90.0 ? MAGERR_I_CFHTLS * FLUX_I_CFHTLS / 1.086 : NULL\"" \
        ocmd="addcol FLUX_Z_CFHTLS     -units \"Jy\" \"MAG_Z_CFHTLS>0.0 && MAG_Z_CFHTLS<90.0 ? 3631.0 * pow(10, MAG_Z_CFHTLS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_Z_CFHTLS  -units \"Jy\" \"MAG_Z_CFHTLS>0.0 && MAG_Z_CFHTLS<90.0 ? MAGERR_Z_CFHTLS * FLUX_Z_CFHTLS / 1.086 : NULL\"" \
        ocmd="addcol FLUX_J_WIRDS      -units \"Jy\" \"MAG_J_WIRDS>0.0  && MAG_J_WIRDS<90.0  ? 3631.0 * pow(10, MAG_J_WIRDS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_J_WIRDS   -units \"Jy\" \"MAG_J_WIRDS>0.0  && MAG_J_WIRDS<90.0  ? MAGERR_J_WIRDS * FLUX_J_WIRDS / 1.086 : NULL\"" \
        ocmd="addcol FLUX_H_WIRDS      -units \"Jy\" \"MAG_H_WIRDS>0.0  && MAG_H_WIRDS<90.0  ? 3631.0 * pow(10, MAG_H_WIRDS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_H_WIRDS   -units \"Jy\" \"MAG_H_WIRDS>0.0  && MAG_H_WIRDS<90.0  ? MAGERR_H_WIRDS * FLUX_H_WIRDS / 1.086 : NULL\"" \
        ocmd="addcol FLUX_K_WIRDS      -units \"Jy\" \"MAG_K_WIRDS>0.0  && MAG_K_WIRDS<90.0  ? 3631.0 * pow(10, MAG_K_WIRDS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_K_WIRDS   -units \"Jy\" \"MAG_K_WIRDS>0.0  && MAG_K_WIRDS<90.0  ? MAGERR_K_WIRDS * FLUX_K_WIRDS / 1.086 : NULL\"" \
        ocmd="addcol FLUX_J_UKIDSS     -units \"Jy\" \"MAG_J_UKIDSS>0.0 && MAG_J_UKIDSS<90.0 ? 3631.0 * pow(10, MAG_J_UKIDSS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_J_UKIDSS  -units \"Jy\" \"MAG_J_UKIDSS>0.0 && MAG_J_UKIDSS<90.0 ? MAGERR_J_UKIDSS * FLUX_J_UKIDSS / 1.086 : NULL\"" \
        ocmd="addcol FLUX_K_UKIDSS     -units \"Jy\" \"MAG_K_UKIDSS>0.0 && MAG_K_UKIDSS<90.0 ? 3631.0 * pow(10, MAG_K_UKIDSS/(-2.5)) : NULL\"" \
        ocmd="addcol FLUXERR_K_UKIDSS  -units \"Jy\" \"MAG_K_UKIDSS>0.0 && MAG_K_UKIDSS<90.0 ? MAGERR_K_UKIDSS * FLUX_K_UKIDSS / 1.086 : NULL\"" \
        omode=out \
        out="combined.fits"





