# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 11:07:59 2018

@author: Thomas Schatz

Testing predictions for minimal pair discrimination 
on American English r/l with w/y and
all consonant contrasts except                                                  `````` r/l average
as controls.

The main function is RL_AmEnglish.

This assumes:
  1. That the pandas.DataFrame specified as argument contains at least
     a'contrast', an 'error' and a 'test language' column.
  2. That items in the 'contrast' column follow a naming scheme
     compatible with scone_phobia.utils.mp_scores.mp_contrast_name
  3. That American English r, l, w, y in the contrast names appear as
     'R', 'L', 'W', 'Y' respectively.
  4. That the 'test language' column for American English test corpora
     (and only for those) contains 'American English'.
  5. That errors should be obtained by grouping together all lines of the
     Dataframe sharing the same values in all columns but 'contrast' and
     'error'.
  6. That scone_phobia.metadata.corpora correctly specifies consonants for
     the 'American English' language.
"""



import scone_phobia.metadata.corpora as corpora
import scone_phobia.utils.mp_scores as mp_scores
import numpy as np
import pandas


def RL_AmEnglish(df):
    """
    Select only r/l and w/y, plus add average on consonant contrasts rows
    TODO? do the two parts using separate functions shared with other analyses
    """
    assert 'test language' in df.columns, df.columns
    assert 'error' in df.columns, df.columns
    assert 'contrast' in df.columns, df.columns
    # rl, wy
    target_contrasts = [mp_scores.mp_contrast_name('R', 'L'), 
                        mp_scores.mp_contrast_name('W', 'Y')]
    ind_AE = df['test language'] == 'American English'
    ind_con = [e in target_contrasts for e in df['contrast']]
   
    df_res = df[ind_AE & ind_con].copy()  # make a copy to avoid side-effects
    # C avg
    # columns on which to average
    cols = list(df.columns)
    del cols[cols.index('contrast')]
    del cols[cols.index('error')]
    df_AE = df[ind_AE]
    AE_C = corpora.consonants('American English')
    RL = mp_scores.mp_contrast_name('R', 'L')
    # keep all consonant contrasts but R/L
    ind_C = [np.all([seg in AE_C for seg in con.split("-")]) and con != RL
                for con in df_AE['contrast']]
    df_C = df_AE[ind_C].groupby(cols, as_index=False).mean()
    df_C['contrast'] = "all_C"    
    
    df_res = pandas.concat([df_res, df_C])    
    df_res = df_res.reset_index(drop=True)
    return df_res
