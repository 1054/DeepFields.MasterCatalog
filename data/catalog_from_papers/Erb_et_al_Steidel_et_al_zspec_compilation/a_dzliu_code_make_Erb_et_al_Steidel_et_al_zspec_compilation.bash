#!/bin/bash
# 
set -e

topcat -stilts tmatchn nin=4 \
        in1="Erb_2006ApJ...646..107E_table1_photometry_converted_Jy.txt" ifmt1=ascii \
        in2="Erb_2006ApJ...646..107E_table3_SED_SFR.txt" ifmt2=ascii \
        in3="Erb_2006ApJ...646..107E_table4_kinematics_Mstar.txt" ifmt3=ascii \
        in4="Erb_2006ApJ...647..128E_table1_zspec.txt" ifmt4=ascii \
        icmd3="delcols \"Mstar\"" \
        matcher=exact \
        values1='ID' values2='ID' values3='ID' values4='ID' \
        suffix1='' suffix2='__dup__2' suffix3='__dup__3' suffix4='__dup__4' \
        join1=always \
        fixcols=dups \
        ocmd="addcol Mstar_SED \"Mstar\"" \
        ocmd="addcol SFR_SED \"SFR__dup__2\"" \
        ocmd="addcol SFR_UV_CORR \"USFR1\"" \
        ocmd="addcol SFR_Ha_CORR \"SFR1\"" \
        ocmd="delcols \"*__dup__* Mstar SFR0 SFR1 USFR0 USFR1 radius_Ha\"" \
        ocmd="replacecol RA \"formatDecimal(RA,\\\"0.000000000\\\")\"" \
        ocmd="replacecol DEC \"formatDecimal(DEC,\\\"+0.00000000\\\")\"" \
        out="Erb_2006ApJ...646..107E_all_in_one.txt" ofmt=ascii
        # 
        # ocmd="delcols \"*__dup__*\"" \
        # 
        # FLUX_U FLUX_G FLUX_R FLUX_J FLUX_Ks 
        # MAG_V_AB MAG_H_Vega MAG_F160W


topcat -stilts tmatchn nin=5 \
        in1="Erb_2006ApJ...646..107E_all_in_one.txt" ifmt1=ascii \
        in2="ForsterSchreiber_2009ApJ...706.1364F_table1_zspec.txt" ifmt2=ascii \
        in3="ForsterSchreiber_2009ApJ...706.1364F_table2_photometry.txt" ifmt3=ascii \
        in4="ForsterSchreiber_2009ApJ...706.1364F_table3_SFR.txt" ifmt4=ascii \
        in5="ForsterSchreiber_2011ApJ...731...65F_table1_HST_photometry_6_LBGs.txt" ifmt5=ascii \
        icmd2="delcols \"Class MAG_K_Vega Parent_Survey_or_Field Ref\"" \
        icmd3="addcol FLUX_B -units \"Jy\" \"MAG_B_AB>0.0 && MAG_B_AB<99.0 ? pow(10,MAG_B_AB/(-2.5))*3631. : NULL\"" \
        icmd3="addcol FLUXERR_B -units \"Jy\" \"MAG_B_AB>0.0 && MAG_B_AB<99.0 ? FLUX_B*MAGERR_B_AB/1.086 : NULL\"" \
        icmd3="delcols \"*_minus_*\"" \
        icmd4="addcol e_SFR -after SFR \"SFR>0.0 ? max(elo_SFR,ehi_SFR) : NULL\"" \
        icmd4="addcol e_Mstar -after Mstar \"Mstar>0.0 ? max(elo_Mstar,ehi_Mstar) : NULL\"" \
        icmd5="addcol FLUX_F160W -units \"Jy\" \"MAG_F160W>0.0 && MAG_F160W<99.0 ? pow(10,MAG_F160W/(-2.5))*3631. : NULL\"" \
        icmd5="addcol FLUXERR_F160W -units \"Jy\" \"MAG_F160W>0.0 && MAG_F160W<99.0 ? FLUX_F160W*MAGERR_F160W/1.086 : NULL\"" \
        matcher=exact \
        values1='ID' values2='ID' values3='ID' values4='ID' values5='ID' \
        suffix1='' suffix2='__dup__2' suffix3='__dup__3' suffix4='__dup__4' suffix5='__dup__5' \
        join1=always \
        fixcols=dups \
        ocmd="addcol Ref_Mstar -after e_Mstar \"Mstar>0.0 ? \\\"ForsterSchreiber+2009\\\" : (Mstar_SED>0.0 ? \\\"Erb+2006\\\" : \\\"\\\")\"" \
        ocmd="replacecol e_Mstar \"Mstar>0.0 ? e_Mstar : (Mstar_SED>0.0 ? NULL : NULL)\"" \
        ocmd="replacecol Mstar \"Mstar>0.0 ? Mstar : (Mstar_SED>0.0 ? Mstar_SED : NULL)\"" \
        ocmd="addcol Ref_SFR -after e_SFR \"SFR>0.0 ? \\\"ForsterSchreiber+2009\\\" : (SFR_SED>0.0 ? \\\"Erb+2006\\\" : \\\"\\\")\"" \
        ocmd="replacecol e_SFR \"SFR>0.0 ? e_SFR : (SFR_SED>0.0 ? NULL : NULL)\"" \
        ocmd="replacecol SFR \"SFR>0.0 ? SFR : (SFR_SED>0.0 ? SFR_SED : NULL)\"" \
        ocmd="replacecol RA \"formatDecimal(RA,\\\"0.000000000\\\")\"" \
        ocmd="replacecol DEC \"formatDecimal(DEC,\\\"+0.00000000\\\")\"" \
        out="Erb_2006ApJ...646..107E_all_in_one_with_ForsterSchreiber_2009_2011.txt" ofmt=ascii


topcat -stilts tmatchn nin=2 \
        in1="Shapley_2005ApJ...626..698S_table2_photometry.txt" ifmt1=ascii \
        in2="Shapley_2005ApJ...626..698S_table3_Mstar.txt" ifmt2=ascii \
        icmd1="addcol RA -after DEC_DMS \"hmsToDegrees(RA_HMS)\"" \
        icmd1="addcol DEC -after RA \"dmsToDegrees(DEC_DMS)\"" \
        matcher=exact \
        values1='ID' values2='ID' \
        suffix1='' suffix2='__dup__2' \
        join1=always \
        fixcols=dups \
        ocmd="addcol MAG_G \"MAG_R>0.0 && MAG_R<99.0 ? MAG_R+G_minus_R : NULL\"" \
        ocmd="addcol MAGERR_G \"MAG_R>0.0 && MAG_R<99.0 ? max(MAGERR_R,e_G_minus_R) : NULL\"" \
        ocmd="addcol MAG_U \"MAG_G>0.0 && MAG_G<99.0 ? MAG_G+U_minus_G : NULL\"" \
        ocmd="addcol MAGERR_U \"MAG_G>0.0 && MAG_G<99.0 ? max(MAGERR_G,e_U_minus_G) : NULL\"" \
        ocmd="addcol MAG_Ks \"MAG_R>0.0 && MAG_R<99.0 ? MAG_R-R_minus_K : NULL\"" \
        ocmd="addcol MAGERR_Ks \"MAG_R>0.0 && MAG_R<99.0 ? max(MAGERR_R,e_R_minus_K) : NULL\"" \
        ocmd="addcol FLUX_R -units \"Jy\" \"MAG_R>0.0 && MAG_R<99.0 ? pow(10,MAG_R/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_R -units \"Jy\" \"MAG_R>0.0 && MAG_R<99.0 ? FLUX_R*MAGERR_R/1.086 : NULL\"" \
        ocmd="addcol FLUX_G -units \"Jy\" \"MAG_G>0.0 && MAG_G<99.0 ? pow(10,MAG_G/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_G -units \"Jy\" \"MAG_G>0.0 && MAG_G<99.0 ? FLUX_G*MAGERR_G/1.086 : NULL\"" \
        ocmd="addcol FLUX_U -units \"Jy\" \"MAG_U>0.0 && MAG_U<99.0 ? pow(10,MAG_U/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_U -units \"Jy\" \"MAG_U>0.0 && MAG_U<99.0 ? FLUX_U*MAGERR_U/1.086 : NULL\"" \
        ocmd="addcol FLUX_Ks -units \"Jy\" \"MAG_Ks>0.0 && MAG_Ks<99.0 ? pow(10,MAG_Ks/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_Ks -units \"Jy\" \"MAG_Ks>0.0 && MAG_Ks<99.0 ? FLUX_Ks*MAGERR_Ks/1.086 : NULL\"" \
        ocmd="addcol FLUX_IRAC1 -units \"Jy\" \"MAG_IRAC1>0.0 && MAG_IRAC1<99.0 ? pow(10,MAG_IRAC1/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_IRAC1 -units \"Jy\" \"MAG_IRAC1>0.0 && MAG_IRAC1<99.0 ? FLUX_IRAC1*MAGERR_IRAC1/1.086 : NULL\"" \
        ocmd="addcol FLUX_IRAC2 -units \"Jy\" \"MAG_IRAC2>0.0 && MAG_IRAC2<99.0 ? pow(10,MAG_IRAC2/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_IRAC2 -units \"Jy\" \"MAG_IRAC2>0.0 && MAG_IRAC2<99.0 ? FLUX_IRAC2*MAGERR_IRAC2/1.086 : NULL\"" \
        ocmd="addcol FLUX_IRAC3 -units \"Jy\" \"MAG_IRAC3>0.0 && MAG_IRAC3<99.0 ? pow(10,MAG_IRAC3/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_IRAC3 -units \"Jy\" \"MAG_IRAC3>0.0 && MAG_IRAC3<99.0 ? FLUX_IRAC3*MAGERR_IRAC3/1.086 : NULL\"" \
        ocmd="addcol FLUX_IRAC4 -units \"Jy\" \"MAG_IRAC4>0.0 && MAG_IRAC4<99.0 ? pow(10,MAG_IRAC4/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_IRAC4 -units \"Jy\" \"MAG_IRAC4>0.0 && MAG_IRAC4<99.0 ? FLUX_IRAC4*MAGERR_IRAC4/1.086 : NULL\"" \
        ocmd="replacecol RA \"formatDecimal(RA,\\\"0.000000000\\\")\"" \
        ocmd="replacecol DEC \"formatDecimal(DEC,\\\"+0.00000000\\\")\"" \
        ocmd="delcols \"*__dup__*\"" \
        out="Shapley_2005ApJ...626..698S_all_in_one.txt" ofmt=ascii


topcat -stilts tmatchn nin=3 \
        in1="Erb_2014ApJ...795...33E_table1_position.txt" ifmt1=ascii \
        in2="Erb_2014ApJ...795...33E_table2_zspec.txt" ifmt2=ascii \
        in3="Erb_2014ApJ...795...33E_table4_HST_photometry.txt" ifmt3=ascii \
        icmd1="addcol RA -after DEC_DMS \"hmsToDegrees(RA_HMS)\"" \
        icmd1="addcol DEC -after RA \"dmsToDegrees(DEC_DMS)\"" \
        icmd3="delcols \"zHa\"" \
        matcher=exact \
        values1='ID' values2='ID' values3='ID' \
        suffix1='' suffix2='__dup__2' suffix3='__dup__3' \
        join1=always \
        fixcols=dups \
        ocmd="addcol FLUX_R -units \"Jy\" \"MAG_R>0.0 && MAG_R<99.0 ? pow(10,MAG_R/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_R -units \"Jy\" \"MAG_R>0.0 && MAG_R<99.0 ? FLUX_R*MAGERR_R/1.086 : NULL\"" \
        ocmd="addcol FLUX_F625W -units \"Jy\" \"MAG_F625W>0.0 && MAG_F625W<99.0 ? pow(10,MAG_F625W/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_F625W -units \"Jy\" \"MAG_F625W>0.0 && MAG_F625W<99.0 ? FLUX_F625W*MAGERR_F625W/1.086 : NULL\"" \
        ocmd="addcol FLUX_F814W -units \"Jy\" \"MAG_F814W>0.0 && MAG_F814W<99.0 ? pow(10,MAG_F814W/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_F814W -units \"Jy\" \"MAG_F814W>0.0 && MAG_F814W<99.0 ? FLUX_F814W*MAGERR_F814W/1.086 : NULL\"" \
        ocmd="addcol FLUX_F160W -units \"Jy\" \"MAG_F160W>0.0 && MAG_F160W<99.0 ? pow(10,MAG_F160W/(-2.5))*3631. : NULL\"" \
        ocmd="addcol FLUXERR_F160W -units \"Jy\" \"MAG_F160W>0.0 && MAG_F160W<99.0 ? FLUX_F160W*MAGERR_F160W/1.086 : NULL\"" \
        ocmd="replacecol RA \"formatDecimal(RA,\\\"0.000000000\\\")\"" \
        ocmd="replacecol DEC \"formatDecimal(DEC,\\\"+0.00000000\\\")\"" \
        ocmd="delcols \"*__dup__*\"" \
        out="Erb_2014ApJ...795...33E_all_in_one.txt" ofmt=ascii
        # 
        #out="Erb_et_al_Steidel_et_al_zspec_compilation_2_Q1700_SSA22a.txt" ofmt=ascii
        # 


topcat -stilts tmatch2 \
        in1="Shapley_2005ApJ...626..698S_all_in_one.txt" ifmt1=ascii \
        in2="Erb_2014ApJ...795...33E_all_in_one.txt" ifmt2=ascii \
        matcher=sky params=1.0 \
        values1='RA DEC' values2='RA DEC' \
        suffix1='' suffix2='__dup__2' \
        join=1and2 \
        find=all \
        ocmd="replacecol RA \"formatDecimal(RA,\\\"0.000000000\\\")\"" \
        ocmd="replacecol DEC \"formatDecimal(DEC,\\\"+0.00000000\\\")\"" \
        out="xmatch12.txt" ofmt=ascii
        # no match


