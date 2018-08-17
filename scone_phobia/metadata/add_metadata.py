# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 09:30:58 2018

@author: Thomas Schatz

Utility functions to extend a dataframe with additional metadata,
e.g. complementing the name of training and test sets with their
respective language and register.
"""


import scone_phobia.metadata.corpora as corpora


def language_register(df):
    """
    Add 'training language', 'test language', 'training register' and 'test register'
    columns to a dataframe.
    This assumes that:
     - the dataframe contains a 'training set' and 'test set' column
     - the sets mentioned in these columns are properly documented in
       the scone_phobia.metadata.corpora module. The only exception is
       if a set is called 'None'. In that case, the new columns will
       be set to 'None' as well.
    """
    df['training language'] = ['None' if e == 'None' else corpora.language(e)
                                for e in df['training set']]
    df['test language'] = ['None' if e == 'None' else corpora.language(e)
                            for e in df['test set']]
    df['training register'] = ['None' if e == 'None' else corpora.register(e)
                                for e in df['training set']]
    df['test register'] = ['None' if e == 'None' else corpora.register(e)
                            for e in df['test set']]
    return df