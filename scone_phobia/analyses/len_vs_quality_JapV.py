# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 10:02:52 2018

@author: Thomas Schatz


Testing predictions for minimal pair discrimination 
on vowel length in Japanese with vowel quality as a control.

The main function is len_vs_quality_JapV.

This assumes:
  1. That the pandas.DataFrame specified as argument contains at least
     a'contrast', an 'error' and a 'test language' column.
  2. That items in the 'contrast' column follow a naming scheme
     compatible with scone_phobia.utils.mp_scores.mp_contrast_name
  3. That Japanese vowels in the contrast names appear as
     'a', 'e', 'i', 'o', 'u' for short vowels and
     'a+H', 'e+H', 'i+H', 'o+H', 'u+H' for long vowels
  4. That the 'test language' column for Japanese test corpora
     (and only for those) contains 'Japanese'.
  5. That errors should be obtained by grouping together all lines of the
     Dataframe sharing the same values in all columns but 'contrast' and
     'error'.
"""


# this is just to use the mp_contrast_name function
# taking two segment names and returning the name of 
# the contrast as specified in the 'contrast' column
# of the mp_error dataframe.
import scone_phobia.utils.mp_scores as mp_scores


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
    # would be cleaner to get that from scone_phobia.metadata.corpora maybe
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
    # columns on which to average
    cols = list(df_len.columns)
    del cols[cols.index('contrast')]
    del cols[cols.index('error')]
    df_avg = df_len.groupby(cols, as_index=False).mean()
    return df_avg


def len_vs_quality_JapV(df):
    assert 'test language' in df.columns, df.columns
    assert 'error' in df.columns, df.columns
    assert 'contrast' in df.columns, df.columns
    return avg_over_groups(select_mp_errors(df))
