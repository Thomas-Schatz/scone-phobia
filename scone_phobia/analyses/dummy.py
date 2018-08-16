# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 10:00:48 2018

@author: Thomas Schatz
"""


from scone_phobia import apply_analysis
import scone_phobia.utils.mp_scores as mp_scores
import scone_phobia.metadata.corpora as corpora
import numpy as np
import pandas
# import corpora


def dummy_analysis(df): return df

##########
## Main ##
##########


model_types = ['dpgmm_vtln_vad', 'AMtri1_sat_small_LMtri1satsmall',
               'mfcc_novtln', 'mfcc_vtln', 'BNF', 'AMtri2_sat_LMmono',
               'AMnnet1_tri2_smbr_LMmono']  # list of models to be analysed

mp_folder = '/Users/admin/Documents/PhD/Code/test/mpscores'
run = lambda: apply_analysis(dummy_analysis, mp_folder, model_types,
                             resampling=False)