# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 14:13:48 2018

@author: Thomas Schatz

Compute similarity between patterns of discrimination errors obtained by
different models on a common test set.

The main function is error_sim.

The similarity used is 1 - angular distance,
where the angular distance is defined as:
    
    2*arccos(cosine similarity)/pi
    
which defines a proper metric taking values between 0 and 1 (the 2 factor
can be used because the distance is computed between vectors of discrimination
errors which are always positive). See wikipedia for more details
(https://en.wikipedia.org/wiki/Cosine_similarity)


This assumes:
  1. That the pandas.DataFrame specified as argument contains at least
     a'contrast', an 'error' and a 'test set' column.
  2. That individual error patterns are obtained by grouping all lines
     sharing the same values in all columns but 'contrast' and 'error'.

"""

import numpy as np
import pandas


def cosine_sim(a, b):
    return np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))

def angular_distance(a, b, eps=10**-9):
    s = cosine_sim(a, b)
    # deal with rounding errors
    if s>1 and (s-1) < eps:
        s=1
    if s<-1 and (-1-s) < eps:
        s=-1
    return 2*np.arccos(s)/np.pi

def angular_sim(a, b):
    return 1-angular_distance(a, b)

def compute_err_sim(df, sim=angular_sim):
    # compute similarity betwen 'error_A' and 'error_B' columns of df
    return pandas.Series({'err_sim' : sim(df['error A'], df['error B'])},
                          index=['err_sim'])


def error_sim(df):
    """
    Main function.
    """
    assert 'test set' in df.columns, df.columns
    assert 'error' in df.columns, df.columns
    assert 'contrast' in df.columns, df.columns
    # First merge on contrast and test set
    merge_cols = ['contrast', 'test set']
    if 'test language' in df.columns:
        merge_cols.append('test language')
    if 'test register' in df.columns:
        merge_cols.append('test register')
    # if there is more metadata derived from test set, could be specified here,
    # but it's not a big deal if it isn't, there just will be some duplicated
    # columns.    
    df = df.merge(df, on=merge_cols, suffixes=(' A', ' B'))
    # Second group by all columns but contrast and error_A/B and get cosine sim
    groupby_cols = list(df.columns)
    del groupby_cols[groupby_cols.index('contrast')]
    del groupby_cols[groupby_cols.index('error A')]
    del groupby_cols[groupby_cols.index('error B')]
    res_df = df.groupby(groupby_cols).apply(compute_err_sim)
    # multi-indices -> cols
    res_df.reset_index(level=res_df.index.names, inplace=True)
    return res_df


"""

Possible extension to consider:
    
    For each possible pair of models, ranking
    contrasts as a function of how much they contribute to the dissimilarity
    in error patterns between the two models.
    
    One way to operationalize: look at (signed) angle change when removing
    contrast of interest. Let's say angle is a0 and we add a contrast with
    associated errA, errB, leading to new angle a1, then:
    
        cos(a0) = np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))
        cos(a1) = (np.dot(a, b) + errA*errB) / (sqrt(||a||^2 + errA^2) * same with b)
        
    Then assuming errA, errB << ||a||, ||b||, cos(a1) denom. is to first order:
    
        ||a||||b|| sqrt(1+errA^2/||a||^2+errB^2/||b||^2)
        
    Then applying developpement of 1/sqrt(1+x) en 0 (1 - x/2), we get:
    
        cos(a1) # (np.dot(a, b) + errA*errB) * [ 1 - .5(errA/||a||)^2 - .5(errB/||b||)^2 ] / (||a||||b||)
        
    i.e. to first order:
    
        cos(a1) # cos(a0) * [ 1 - .5(errA/||a||)^2 - .5(errB/||b||)^2 ] +  errA*errB /(||a||||b||)
    
    We can rewrite ||a|| and ||b|| as resp. N*mA, N*mB where N is the number of
    contrasts (excluding the one we're adding) and mA, mB are the average
    errors for modelA, resp. model B, on these contrasts. Let us then define
    rA := errA/mA the ratio of errA to the average error on other contrasts for
    model A and similarly rB:= errB/mB. We get:

         cos(a1) # cos(a0) * [ 1 - rA^2/(2N^2) - rB^2/(2N^2) ] +  rA*rB/N^2
         
         
    For small angles a0, a1, we get to first order:

       1-a1 # (1-a0) * [ 1 - rA^2/(2N^2) - rB^2/(2N^2) ] +  rA*rB/N^2
       a1-a0 # [1-a0] [rA^2/(2N^2) + rB^2/(2N^2)] - rA*rB/N^2
       a1-a0 # 1/(2N^2) * [(rA-rB)^2 - a0[rA^2+rB^2]]
      
    Note that the second term suggests there is an effect of adding dimensions
    (contrasts), maybe some sort of uniformisation effect related to the curse
    of dimensionality. Maybe there is some sort of principled way of correcting
    for this?

    We have, in particular:    
    
     a1-a0 #< 1/(2N^2) * (rA-rB)^2

    This suggests to rank contrasts based on (rA-rB)^2. 
    
    This might give uninformative results if the errors are not well estimated
    and is probably unstable for very small errors. It might be a good idea to
    do it on broad classes of interest to make sure estimates are stable and/or
    to plot the values obtained on a correlation plot with conservative
    confidence intervals.
    
    A completely different but perhaps easier approach to the same problem:
    do GLM modeling of the ABX errors and look for the regression factors
    driving cross-linguistic differences.
    
"""