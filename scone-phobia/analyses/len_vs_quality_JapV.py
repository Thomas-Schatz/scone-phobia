# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 10:02:52 2018

@author: Thomas Schatz


Testing predictions for minimal pair discrimination 
on vowel length in Japanese with vowel quality as a control.
"""

import phonediscri_byspkcontext_mpscores as mp_scores
import ABXresults_management as res_manager


############################
## Data-fetching functions #
############################

def select_mp_errors(df):
    """
    Select only vowel length/quality minimal pairs in df
    and add a 'contrast type' column indicating 'duration'
    or 'quality' for each contrast
    
    Input: 
        df : pandas.Dataframe  with a 'test language' and 'contrast' column
    Output:
        df_out : pandas.Dataframe with only Japanese vowel length and vowel
                    quality contrasts, as indicated by a new
                    'contrast type' column
    """
    Vquals = ['a', 'e', 'i', 'o', 'u']
    duration = [mp_scores.mp_contrast_name(V, V+'+H') for V in Vquals]
    quality = [mp_scores.mp_contrast_name(V1, V2)
                for V1 in Vquals for V2 in Vquals if V1<V2] + \
              [mp_scores.mp_contrast_name(V1+'+H', V2+'+H')
                  for V1 in Vquals for V2 in Vquals if V1<V2]
    target_contrasts = duration + quality
    ind_jap = df['test language'] == 'Japanese'
    ind_con = [e in target_contrasts for e in df['contrast']]
    df_out = df[ind_jap & ind_con].copy()  # make a copy to avoid side-effects
    df_out = df_out.reset_index(drop=True)  # get a simple index
    # add contrast type column  
    df_out['contrast type'] = ['length' if e in duration else 'quality'
                                                for e in df_out['contrast']]
    return df_out


def avg_over_groups(df_len):
    """
    Aggregate minimal pair errors over all length, resp. all quality contrasts
    """
    cols = ['model type', 'train set', 'test set', 'dissimilarity']
    cols = cols + ['train language', 'test language',
                   'train register', 'test register']
    cols = cols + ['contrast type']
    df_avg = df_len.groupby(cols, as_index=False).mean()
    return df_avg


##########
## Main ##
##########


model_types = ['dpgmm_vtln_vad', 'AMtri1_sat_small_LMtri1satsmall',
               'mfcc_novtln', 'mfcc_vtln', 'BNF', 'AMtri2_sat_LMmono',
               'AMnnet1_tri2_smbr_LMmono']  # list of models to be analysed

root = '/Users/admin/Documents/PhD/Code/perceptual-tuning-results/ABX/'  #HMMvsDNN/tri2vsnnet1/'
resampling = True  # set to True to get errobars
                    # you need to have run resample_mp_score.py before


analysis = lambda df: avg_over_groups(select_mp_errors(df))
analysis_name = "len_vs_quality_JapV"
get_results = lambda: res_manager.get_results(analysis, analysis_name, root,
                                              model_types, resampling)
