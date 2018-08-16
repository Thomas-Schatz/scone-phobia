# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 11:07:59 2018

@author: Thomas Schatz
"""


from scone_phobia import apply_analysis
import scone_phobia.utils.mp_scores as mp_scores
import numpy as np
import pandas
import corpora


def AE_rl(df):
    """
    Select only r/l and w/y, plus add average on consonant contrasts rows
    TODO? do the two parts using separate functions shared with other analyses
    """
    # rl, wy
    target_contrasts = [mp_scores.mp_contrast_name('R', 'L'), 
                        mp_scores.mp_contrast_name('W', 'Y')]
    ind_AE = df['test language'] == 'American English'
    ind_con = [e in target_contrasts for e in df['contrast']]
   
    df_res = df[ind_AE & ind_con].copy()  # make a copy to avoid side-effects
    # C avg
    cols = ['model type', 'train set', 'test set', 'dissimilarity']
    cols = cols + ['train language', 'test language',
                   'train register', 'test register']
    df_AE = df[ind_AE]
    AE_C = corpora.consonants('American English')
    ind_C = [np.all([seg in AE_C for seg in con.split("-")])
                for con in df_AE['contrast']]
    df_C = df_AE[ind_C].groupby(cols, as_index=False).mean()
    df_C['contrast'] = "all_C"    
    
    df_res = pandas.concat([df_res, df_C])    
    df_res = df_res.reset_index(drop=True)
    return df_res


##########
## Main ##
##########


model_types = ['dpgmm_vtln_vad', 'AMtri1_sat_small_LMtri1satsmall',
               'mfcc_novtln', 'mfcc_vtln', 'BNF', 'AMtri2_sat_LMmono',
               'AMnnet1_tri2_smbr_LMmono']  # list of models to be analysed

root = '/Users/admin/Documents/PhD/Code/perceptual-tuning-results/ABX/'  #HMMvsDNN/tri2vsnnet1/'
resampling = True  # set to True to get errobars
                    # you need to have run resample_mp_score.py before


analysis = lambda df: AE_rl(df)
analysis_name = "RL_AmEnglish"
get_results = lambda: apply_analysis(analysis, analysis_name, root,
                                     model_types, resampling)