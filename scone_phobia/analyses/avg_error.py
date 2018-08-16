# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 12:01:02 2018

@author: Thomas Schatz

Average errors on C, V or all contrasts (excluding silence/noise marker)
"""


from scone_phobia import apply_analysis
import scone_phobia.metadata.corpora as corpora
import numpy as np
import pandas
# import corpora


def average_error(df):
    #TODO get all language and do for loop with call to appropriate char sets
    # loop over grand average, C average and V average
    test_langs = np.unique(df['test language'])

    for lang in test_langs:
        ind_lang = df['test language'] == lang
        # ad hoc cols?
        cols = ['model type', 'train set', 'test set', 'dissimilarity']
        cols = cols + ['train language', 'test language',
                       'train register', 'test register']
        df_lang = df[ind_lang]
        lang_C = corpora.consonants(lang)
        lang_V = corpora.vowels(lang)
        all_seg = lang_C +lang_V
        dfs = []
        for segs, con_type in [(lang_C, 'C'), (lang_V, 'V'), (all_seg, 'all')]:
            ind_segs = [np.all([seg in segs for seg in con.split("-")])
                                                for con in df_lang['contrast']]
            
            df_langseg = df_lang[ind_segs].groupby(cols, as_index=False).mean()
            df_langseg['contrast type'] = con_type
            dfs.append(df_langseg)
    df_res = pandas.concat(dfs)    
    df_res = df_res.reset_index(drop=True)
    return df_res


##########
## Main ##
##########

# from python
import scone_phobia.analyses.avg_error as avg_error
import scone_phobia.plots.avg_error as plt_avg_error
mp_folder = ...
avg_error.run(mp_folder, ...)
plt_avg_error.plot(...)



mp_folder = '/Users/admin/Documents/PhD/Code/test/mpscores'

model_types = ['dpgmm_vtln_vad', 'AMtri1_sat_small_LMtri1satsmall',
               'mfcc_novtln', 'mfcc_vtln', 'BNF', 'AMtri2_sat_LMmono',
               'AMnnet1_tri2_smbr_LMmono']  # list of models to be analysed

# set to True to get errobars, you need to have run resample_mp_score.py before
resampling = True  
analysis = lambda df: average_error(df)

model_types = ['dpgmm_vtln_vad', 'AMtri1_sat_small_LMtri1satsmall',
               'mfcc_novtln', 'mfcc_vtln', 'BNF', 'AMtri2_sat_LMmono',
               'AMnnet1_tri2_smbr_LMmono']  # list of models to be analysed

res = apply_analysis(analysis, mp_folder, model_types,
                     resampling=resampling, analysis_folder='')
df.save(res)



