# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 11:24:31 2018

@author: Thomas Schatz

General-purpose utilities related to computing minimal-pair ABX
phone discrimination errors in a task:
    ON phone BY speaker, preceding and following phonetic context.

The names of the columns in the item file that were used to generate the 
ABX task should be specified appopriately in the '../config.yml' config file.
You can use the config file template at '../config.yml.example' for inspiration.

Part of this code could probably be generalized to analysing results from 
other ABX tasks. If we need to do that, Not sure if we should try to increase
the scope of the current library, if we should do two independent libraries with
some (a lot of?) redundant code or if we should have an independent abstract
library being called by several libraries applied to particular tasks.
"""

import numpy as np
import ast
import pandas
import os
import os.path as path
import pickle
import oyaml as yaml


def load_cfg_from_file(f):
    # decorator that will load keyword cfg argument
    # from "../config.yml" unless it is specified explicitly
    def wrapper(*args, **kwargs):
        if not('cfg' in kwargs) or (kwargs['cfg'] is None):
            dir = path.dirname(os.path.realpath(__file__))
            cfg_file = path.join(dir, "..", "config.yml")
            with open(cfg_file, 'r') as ymlfile:
                kwargs['cfg'] = yaml.load(ymlfile, Loader=yaml.Loader)['results-file-columns']
        return f(*args, **kwargs)
    return wrapper


#######################
# Loading raw results #
#######################
# Should be changed if the format of results produced by ABXpy changes

def parse_by(df, by_columns):
    arr = np.array([e for e in map(ast.literal_eval, df['by'])])
    for i, by in enumerate(by_columns):
        assert not by in df
        df[by] = arr[:,i]
    del df['by']
    return df


def load_df(result_file, cols):
    df = pandas.read_csv(result_file, sep='\t')
    df = parse_by(df, cols)
    return df


#############################
# Getting symetrized scores #
#############################
# this would need to be done differently for across speaker tasks

def add_contrast_col(df, col_phone1, col_phone2):
    # a utility function
    if not('contrast' in df):
        contrast_name = lambda p1, p2: p1+'-'+p2 if p1<=p2 else p2+'-'+p1
        df['contrast'] = [contrast_name(p1,p2) for p1, p2 in zip(df[col_phone1],
                                                                 df[col_phone2])]
    return df


@load_cfg_from_file
def drop_asymetric_scores(df, reg_cols, cfg=None):
    l = len(df)
    df = add_contrast_col(df, cfg['phone_1'], cfg['phone_2'])
    groups = df.groupby(['contrast'] + reg_cols, as_index=False)
    df = groups.filter(lambda x: len(x) == 2)
    if len(df) != l:
        dl = l-len(df)
        print('{} scores had no matching symetric, they were dropped'.format(dl))
    return df


@load_cfg_from_file
def symetrize_scores(df, reg_cols, cfg=None):
    df = add_contrast_col(df, cfg['phone_1'], cfg['phone_2'])
    groups = df.groupby(['contrast'] + reg_cols, as_index=False)
    # check that all results can be symetrized
    # this should be guaranteed since we use drop_asymetric_scores above
    wrong_lengths = {(g, df_g) for g, df_g in groups if len(df_g) != 2}   
    assert not(wrong_lengths), wrong_lengths
    return groups['score'].mean()


#################################
# Computing minimal-pair scores #
#################################


def ordered_aggregation(df, *agg_cols_list):
    # utility function to do structured averaging of scores
    for agg_cols in agg_cols_list:
        cols = ['contrast'] + agg_cols
        groups = df.groupby(cols, as_index=False)
        df = groups['score'].mean()
    return df


@load_cfg_from_file
def minimal_pair_scores_spk_first(df, cfg=None):
    """
    Aggregate scores over all talkers and contexts
    We aggregate on speakers first, then contexts.
    Probably easier to interpret, but makes it necessary to use resampling
    to get error bars based on speaker variability.
    """
    spk_agg_cols = [cfg['prev-phone'], cfg['next-phone']]
    context_agg_cols = []
    df = ordered_aggregation(df, spk_agg_cols, context_agg_cols)
    return df


@load_cfg_from_file
def minimal_pair_scores_context_first(df, cfg=None):
    """
    Aggregate scores over all talkers and contexts
    We aggregate on context first, then speakers.
    Might be less stable, but easier to get variability
    estimates based on speaker differences.
    """
     # aggregate on contexts
    context_agg_cols = [cfg['speaker']]
    spk_agg_cols = []
    df = ordered_aggregation(df, context_agg_cols, spk_agg_cols)
    return df


@load_cfg_from_file
def minimal_pair_scores_by_context(df, cfg=None):
    spk_agg_cols = [cfg['prev-phone'], cfg['next-phone']]
    df = ordered_aggregation(df, spk_agg_cols)
    return df


@load_cfg_from_file
def minimal_pair_scores_by_spk(df, cfg=None):
    context_agg_cols = [cfg['speaker']]
    df = ordered_aggregation(df, context_agg_cols)
    return df


######################
# Querying mp scores #
######################

def mp_contrast_name(p1, p2):
    if p1<=p2:
        name = p1+'-'+p2
    else:
        name = p2+'-'+p1
    return name


def get_mp_error(df, phone_1, phone_2):
    """Function to query a particular minimal-pair ABX error (in %)"""
    contrast = mp_contrast_name(phone_1, phone_2)
    ix = np.where(df['contrast'] == contrast)[0]
    if ix.size == 0:
        print("No entry available for minimal-pair {}".format(contrast))
        error = np.nan
    else:
        line = df.iloc[ix]
        error = line['error']
        assert(len(error) <= 1), ("More than one entry "
                                  "for minimal-pair: {}").format(contrast)                        
        error = error.iloc[0]
    return error


@load_cfg_from_file
def get_mp_con_error(df, phone_1, phone_2, prev_con, next_con):
    """Function to query a particular minimal-pair ABX error (in %)"""
    contrast = mp_contrast_name(phone_1, phone_2)
    ix = np.where((df['contrast'] == contrast) & (df[cfg['prev-phone']] == prev_con) & (df[cfg['next-phone']] == next_con))[0]
    if ix.size == 0:
        print("No entry available for minimal-pair {} in context {}".format(contrast, "-".join(prev_con, next_con)))
        error = np.nan
    else:
        line = df.iloc[ix]
        error = line['error']
        assert(len(error) <= 1), ("More than one entry "
                                  "for minimal-pair {} in context {}").format(contrast, "-".join(prev_con, next_con))                        
        error = error.iloc[0]
    return error


@load_cfg_from_file
def get_mp_spk_error(df, phone_1, phone_2, spk):
    """Function to query a particular minimal-pair ABX error (in %)"""
    contrast = mp_contrast_name(phone_1, phone_2)
    ix = np.where((df['contrast'] == contrast) & (df[cfg['speaker']] == spk))[0]
    if ix.size == 0:
        print("No entry available for minimal-pair {} for speaker {}".format(contrast, spk))
        error = np.nan
    else:
        line = df.iloc[ix]
        error = line['error']
        assert(len(error) <= 1), ("More than one entry "
                                  "for minimal-pair {} for speaker {}").format(contrast, con)                        
        error = error.iloc[0]
    return error


#####################################
# Precomputing and saving mp scores #
#####################################

@load_cfg_from_file
def precompute_mp_scores(in_folder, out_folder, mp_type='spk_first', filt=None, cfg=None):
    """
    Function to precompute minimal-pair scores for all results file in a folder    
        in_folder : str, folder containing results files from ABXpy.analyze
        out_folder : str, folder where to put pickles containing the mp scores
        mp_type : specify how to compute minimal-pair scores
        filt : (str -> bool) function, takes an ABXpy results filename 
                without the extension and decides whether to extract mp scores
                for that file based on the name
    """
    if mp_type == 'spk_first':
        minimal_pair_scores = minimal_pair_scores_spk_first
    elif mp_type == 'context_first':
        minimal_pair_scores = minimal_pair_scores_context_first
    elif mp_type == 'by_spk':
        minimal_pair_scores = minimal_pair_scores_by_spk
    elif mp_type == 'by_context':
        minimal_pair_scores = minimal_pair_scores_by_context
    else:
        raise ValueError("Unsupported mp type {}".format(mp_type))
    if filt is None:
        filt = lambda x: True
    reg_cols = list(cfg.values())[2:]  # this relies on cfg being **ordered**
    for f in os.listdir(in_folder):
        model, ext = path.splitext(f)
        if ext == '.txt' and filt(model):
            res_file = path.join(out_folder, model+'.pickle')
            if path.exists(res_file):
                raise IOError(("Minimal pair file "
                               "already exists: {}").format(res_file))
            df = load_df(path.join(in_folder, f), reg_cols)
            df = drop_asymetric_scores(df, reg_cols)
            df = symetrize_scores(df, reg_cols)
            df = minimal_pair_scores(df)
            with open(res_file, 'wb') as fh:
                pickle.dump(df, fh)


###########################
# Loading saved mp scores #
###########################

def load_mp_errors(folder, get_metadata,
                   filt=None, encoding=None, boot_batch_ind=None,
                   boot_df=None, return_raw_df=False):
    """
    Load and concatenate together minimal-pair error dataframes from a folder
    containing pickled versions of these dataframes.
    
    The get_metadata function takes the results-file path as input and returns
    a list of key, value pairs describing the content of that file (metadata).
    This metadata is then added to the output dataframe.
    The same kind of metadata should be provided for all files considered.
    
    If not all dataframes are needed, the 'filt' argument can be used to select
    the desired ones based on filename.
    
    If the pickles were saved with python2 and are loaded in python3 etc., 
    the 'encoding' argument can be passed to pickle.load to ensure
    compatibility.
    
    If the pickled data correspond to whole batches of resampled data a
    specific resample can be selected by specifying 'boot_batch_ind'
    (between 0 and 49 included for batches of size 50). To select only specific
    batches, use 'filt' appropriately.  
    
    boot_df can be used to avoid re-loading again and again the same data
    when resamples for several batches are stored together. It is the caller's
    responsibility to make sure boot_df contains the right data.

    return_raw_df can be used to get the raw data (useful in conjunction with
    boot_df)
    """
    if filt is None:
        filt = lambda x: True
    dfs = []
    if return_raw_df:
        df_raws = {}
    for f in os.listdir(folder):
        model, ext = path.splitext(f)
        if ext == '.pickle' and filt(model):
            if not(boot_df is None):
                    df_raw = boot_df[model]
            else:
                with open(path.join(folder, f), 'rb') as fh:
                    if encoding is None:
                        df_raw = pickle.load(fh)
                    else:
                        # allow hacks to handle pickles saved from python2
                        df_raw = pickle.load(fh, encoding=encoding)
            if not(boot_batch_ind is None):
                 # if bootstrap resample select desired resample only
                df_model = df_raw[boot_batch_ind]
            else:
                df_model = df_raw
            metadata = get_metadata(path.join(folder, f))
            for name, value in metadata:
                df_model[name] = value
            dfs.append(df_model)
            if return_raw_df:
                df_raws[model] = df_raw
    df = pandas.concat(dfs)
    # convert scores to error rates in %
    df['error'] = 100*(1-df['score'])
    del df['score']
    if return_raw_df:
        return df, df_raws
    else:
        return df


##################################
# Resampling minimal-pair scores #
##################################
# This is currently only supported for minimal pairs
# averaged on spk and context (in that order, otherwise there
# is no need to resample)
# (the code might actually produced something meaningful in
# other cases, but this is untested and would require 
# changing the call to minimal_pair_scores_spk_first
# in resample_mp_score_within_speakers)

def resample(items, nb_resamples):
    """
    Get bootstrap resamples from a 1-d numpy array of items.
    """ 
    resamples = []
    for i in range(nb_resamples):
        resamples.append(np.random.choice(items, len(items)))
    resamples = np.row_stack(resamples)
    return resamples


@load_cfg_from_file
def resample_mp_score_within_speakers(df, nb_resamples, reg_cols, mp_type='spk_first', cfg=None):
    """
    Resample minimal-pair scores obtained
    in a within speaker task over speakers.
    """
    if mp_type != 'spk_first':
        raise ValueError("Resampling over speaker only supported for minimal pairs"
                         "averaged on spk and context, in that order.")
    speaker_col = cfg['speaker']
    spk_resamples = resample(np.unique(df[speaker_col]), nb_resamples)     
    spk_groups = df.groupby(speaker_col, as_index=False)
    spk_id, spk_data = list(zip(*spk_groups))  # list of pairs to pair of lists
    mp_scores = []
    for i, spk_resample in enumerate(spk_resamples):  # iterate on array rows
        print(('Getting mp-scores for resample '
               '{} over {}').format(i+1, nb_resamples))
        resampled_data = []
        for j, spk in enumerate(spk_resample):
            spk_ix = spk_id.index(spk)
            spk_df = spk_data[spk_ix].copy()
            spk_df[speaker_col] = str(j)
            resampled_data.append(spk_df)
        resampled_data = pandas.concat(resampled_data)
        resampled_data = drop_asymetric_scores(resampled_data, reg_cols)
        mp_scores.append(minimal_pair_scores_spk_first(symetrize_scores(resampled_data,
                                                                        reg_cols)))
    return mp_scores



#########################################
# Loading resampled minimal-pair scores #
#########################################
    
def load_resampled_mp_errors(folder, get_metadata, bootid,
                             filt=None, encoding=None,
                             nboot=1000, batchsize=50,
                             df_raws=None):
    """
    Load and concatenate together a specific resample of minimal-pair error
    from a folder containing pickled versions of these. 
    
    nboot and batchsize should be compatible with parameters used with
    resample_mp_score.py.
    """
    assert bootid < nboot * batchsize # bootid is 0-indexed
    batchid = bootid // batchsize + 1  # 1-indexed
    index_in_batch = bootid % batchsize # 0-indexed
    # make sure to consider only files corresponding to desired batch
    if filt is None:
        filt = lambda x: True
    augmented_filt = lambda x, f=filt: f(x) and \
                               (x.split('__')[-1] == 'batch' + str(batchid))
    df, df_raws = load_mp_errors(folder, get_metadata,
                                 filt=augmented_filt, encoding=encoding,
                                 boot_batch_ind=index_in_batch,
                                 boot_df=df_raws,
                                 return_raw_df=True)
    df['boot ID'] = bootid  # add a bootid column
    return df, df_raws


###########################################
# Performing an analysis on all resamples #
###########################################

def resample_analysis(analysis, resampled_mp_folder, get_metadata,
                      filt=None, encoding=None, add_metadata=None,
                      nboot=1000, batchsize=50, verbose=0):
    """
    Carry out the same analysis on various resampled versions of minimal pair
    ABX scores.
        Input: 
            analysis : (pandas.Dataframe -> E) function where E can be any
                       type of analysis results
           resampled_mp_folder : str, folder where minimal pair scores for
                                   different data resamples have beens stored
           get_metadata : (str -> (name, value) list) function getting the
                           properties of each result file in
                           resampled_mp_folder from their file path
        Output:
            resampled_res : list of elements from E of size nboot
            
    """
    resampled_res = []
    for i in range(nboot):
        if verbose > 1:
            if i % (nboot//10) == 0:
                print(("{}% of all bootstraps computed").format(100*i//nboot))
        if i % batchsize == 0:   
            df_raws = None
        df, df_raws = load_resampled_mp_errors(resampled_mp_folder,
                                               get_metadata,
                                               i,
                                               filt=filt,
                                               encoding=encoding,
                                               nboot=nboot,
                                               batchsize=batchsize,
                                               df_raws=df_raws)
        if not(add_metadata is None):
            df = add_metadata(df)
        resampled_res.append(analysis(df))
    return resampled_res


def resample_analysis_cached(resampling_file, analysis,
                             resampled_mp_folder=None, get_metadata=None,
                             filt=None, encoding=None, add_metadata=None,
                             nboot=1000, batchsize=50, verbose=0):
    """
    Same as resample_analysis, but caching the results in intermediate files
    for quick re-use.
    
    This assumes that the output of the analysis is pickable.
    """
    if path.exists(resampling_file):
        if verbose > 0:
            print(("Using existing {} "
                   "Delete this file if you want to recompute it"
                   ).format(resampling_file))
    else:
        if verbose > 0:
            print(("No {} file found, "
                   "computing it"
                   ).format(resampling_file))
        assert not(resampled_mp_folder is None) and not(get_metadata is None)
        resampled_res = resample_analysis(analysis, resampled_mp_folder, 
                                          get_metadata, filt=filt,
                                          encoding=encoding,
                                          add_metadata=add_metadata,
                                          nboot=nboot, batchsize=batchsize,
                                          verbose=verbose)
        with open(resampling_file, 'wb') as fh:
            pickle.dump(resampled_res, fh)      
    with open(resampling_file, 'rb') as fh:
        resampled_res = pickle.load(fh)
    return resampled_res


def estimate_std(df, boot_df, resampled_cols=None):
    """
    Estimate standard deviations of some computed values from resamplings
        resampled_cols: should contain all columns whose value
            was being resampled (default value: ['error'])
    """
    if resampled_cols is None:
        resampled_cols = ['error']
    boot_cols = ["batch size", "batch ID", "boot ID"]
    grouping_cols = set(boot_df.columns).difference(boot_cols+resampled_cols)
    grouping_cols = list(grouping_cols)
    # compute standard deviation estimates of resampled_cols
    df_std = boot_df.groupby(grouping_cols, as_index=False).var()
    df_std["std"] = np.sqrt(df_std["error"])
    for col in boot_cols+resampled_cols:
        del df_std[col]
    df = pandas.merge(df, df_std, on=grouping_cols)
    return df

