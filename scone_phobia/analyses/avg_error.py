# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 12:01:02 2018

@author: Thomas Schatz

Average errors on C, V or all contrasts (excluding silence/noise marker)

This assumes:
  1. That the pandas.DataFrame specified as argument contains at least
     a'contrast', an 'error' and a 'test language' column.
  2. That scone_phobia.metadata.corpora specifies vowels and consonants for all
     corpora appearing in the 'test language' column.
  3. That errors should be obtained by grouping all lines
     sharing the same values in all columns but 'contrast' and 'error'
     together.
"""


import scone_phobia.metadata.corpora as corpora
import numpy as np
import pandas


def average_error(df):
    assert 'test language' in df.columns
    assert 'error' in df.columns
    assert 'contrast' in df.columns
    avg_dfs = []
    # columns on which to average
    cols = list(df.columns)
    del cols[cols.index('contrast')]
    del cols[cols.index('error')]
    # iterate over test languages
    test_langs = np.unique(df['test language'])  
    for lang in test_langs:
        # get relevant sub-dataframe
        ind_lang = df['test language'] == lang
        df_lang = df[ind_lang]
        # get segment types for lang
        lang_C = corpora.consonants(lang)
        lang_V = corpora.vowels(lang)
        all_seg = lang_C +lang_V
        # for each segment type, get average errors
        for segs, seg_type in [(lang_C, 'C'), (lang_V, 'V'), (all_seg, 'all')]:
            # get indices of contrasts involving two segments of desired type
            ind_segs = [np.all([seg in segs for seg in con.split("-")])
                                                for con in df_lang['contrast']]
            # average over those contrasts based on groups defined by cols
            avg = df_lang[ind_segs].groupby(cols, as_index=False).mean()
            avg['contrast type'] = seg_type
            avg_dfs.append(avg)
    res_df = pandas.concat(avg_dfs)    
    res_df = res_df.reset_index(drop=True)
    return res_df
