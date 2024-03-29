# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 10:59:28 2018

@author: Thomas Schatz

Code for managing the analysis of a set of ABXpy minimal-pair scores 
for ABX tasks with the following structure:
  ON phone BY speaker, previous and following phonetic context)

The main function is apply_analysis, see readme.md for usage example.

In the current implementation, the metadata associated with each minimal-pair
file can be stored directly in the name of the file, following a scheme described below.
Note that this scheme is parameterized by the 'primary-metadata' section of
the config file.
At minima, the filename should be sufficient to deduce all relevant metadata for carrying
out the analyses and plots.
The scone_phobia/metadata folder can be used to store information associating filename
components with further metadata. It can be useful to keep filenames from getting too long.

This code requires a folder where pickles containing the minimal-pair scores are stored.
If resampling of the scores is needed (e.g. to obtain estimate of variability for
the analysis results), this folder should also contain a 'resampling' subfolder
where pickles containing resample of the minimal-pair scores are stored.

These minimal-pair scores pickles can be obtained with precompute_mp_scores.py
and resample of those with resample_mp_scores.py. Note that both these scripts
will name pickles based on the name of the original ABXpy results filename,
so it's probably a good idea to name those original results files in accordance
with the naming scheme described below.

Part of this code could probably be generalized to analysing results from 
other ABX tasks. If we need to do that, Not sure if we should try to increase
the scope of the current library, if we should do two independent libraries with
some (a lot of?) redundant code or if we should have an independent abstract
library being called by several libraries applied to particular tasks.
"""

import pandas
import os
import os.path as path
import scone_phobia.utils.mp_scores as mp_scores
import yaml


def load_cfg_from_file(f):
    # decorator that will load keyword cfg argument
    # from "../config.yml" unless it is specified explicitly
    def wrapper(*args, **kwargs):
        if not('cfg' in kwargs) or (kwargs['cfg'] is None):
            dir = path.dirname(path.realpath(__file__))
            cfg_file = path.join(dir, "..", "config.yml")
            with open(cfg_file, 'r') as ymlfile:
                kwargs['cfg'] = yaml.load(ymlfile, Loader=yaml.Loader)['primary-metadata']
        return f(*args, **kwargs)
    return wrapper


"""
Filename parsing utilities

Parse filenames for ABX results files and derivatives based on the 'primary-metadata'
specified in '../config.yml'.

Filenames (without the extension) should be of the form:

    Property1valueProperty1key__Property2valueProperty2key__...___PropertyNvaluePropertyNkey.extension

where the property values and keys should not contain any double underscores and
where the property keys should correspond to the keys in the 'primary-metadata' 
section of the '../config.yml' file. The extension can be whatever file extension
is appropriate. For example the following would be valid filenames for the 'primary-metadata'
section of the config file template ('../config.yml.example'):

    HMM-GMMmodel__WSJtrain__CSJtest__KLdis.pickle
    HMM-GMMmodel__WSJtrain__CSJtest__KLdis.txt
    MFCCmodel__Nonetrain__CSJtest__COSdis.pickle

The first one, for example, would be parsed into the following list of pairs:

    [('model type', 'HMM-GMM'),
     ('training set', 'WSJ'),
     ('test set', 'CSJ'),
     ('dissimilarity', 'KL')]

For bootstrap related files, filenames will look like:

    HMM-GMMmodel__WSJtrain__CSJtest__KLdis__batchsize50__batch3.pickle

where the number after 'batchsize' indicates the size of the resampling
batches and the number after 'batch' is the batch ID for this particular file.
For these files, the resampling batch size and batch ID are also
returned.
"""

def suffix_split(token, cfg, err_message):
    """
    Helper function for parsing filenames.
    Looking for a key from cfg that would be
    a suffix of token. There should be one
    and only one.
    """
    matches = []
    for key in cfg:
        if len(token) >= len(key):
            if token[-len(key):] == key:
                matches.append((key, token[:-len(key)]))
    assert len(matches) == 1, err_message
    return matches[0]


@load_cfg_from_file
def parse_res_fname(fpath, cfg=None):
    name, _ = path.splitext(path.split(fpath)[1])
    err_message = ("Results filename {} is not correctly formatted."
                   " Check your config file and "
                   "formatting instructions in analyze_mp_scores.py."
                  ).format(name)
    N = len(cfg)
    tokens = name.split('__')
    assert len(tokens) == N, err_message
    used_keys = []
    res = []
    for token in tokens:
        key, value = suffix_split(token, cfg, err_message)
        assert not key in used_keys, err_message
        used_keys.append(key)
        res.append((cfg[key], value))
    return res


@load_cfg_from_file
def parse_bootres_fname(fpath, cfg=None):
    name, _ = path.splitext(path.split(fpath)[1])
    err_message = ("Bootstrap results filename filename {} is not correctly"
                   " formatted. Check your config file and "
                   "formatting instructions in analyze_mp_scores.py."
                  ).format(name)
    N = len(cfg)
    tokens = name.split('__')
    assert len(tokens) == N+2, err_message
    properties = parse_res_fname('__'.join(tokens[:N]), cfg=cfg)
    batch = tokens[-1]
    assert len(batch) >= 5 and batch[:5] == 'batch', batch
    batch = int(batch[5:])
    batchsize = tokens[-2]
    assert len(batchsize) >= 9 and batchsize[:9] == 'batchsize', batchsize
    batchsize = int(batchsize[9:])
    properties.append(('batch ID', batch))
    properties.append(('batch size', batchsize))
    return properties



############################
## Fetch and analyse data  #
############################

def fetch_data(analysis, mp_folder, filt=None, encoding=None,
               add_metadata=None):
    """Use the above to get just the right data"""
    get_metadata = lambda x, parse=parse_res_fname: parse(x)
    df = mp_scores.load_mp_errors(mp_folder,
                                  get_metadata,
                                  filt=filt,
                                  encoding=encoding) # load all mp scores in a big df
    if not(add_metadata is None):
        df = add_metadata(df)
    df = analysis(df)
    return df


def fetch_resampled_data(analysis,
                         resampling_file=None,
                         resampled_mp_folder=None,
                         filt=None,
                         encoding=None,
                         add_metadata=None,
                         verbose=0):
    # Getting resampled minimal-pair scores to estimate variability.
    # This can take time so if resampling_file is not None,
    # results are saved once they are computed
    get_metadata = lambda x, parse=parse_bootres_fname: parse(x)
    if resampling_file is None:
        boot_dfs = mp_scores.resample_analysis(analysis,
                                               resampled_mp_folder,
                                               get_metadata,
                                               filt=filt,
                                               encoding=encoding,
                                               add_metadata=add_metadata,
                                               verbose=verbose)
    else:
        boot_dfs = mp_scores.resample_analysis_cached(resampling_file,
                                                      analysis,
                                                      resampled_mp_folder,
                                                      get_metadata,
                                                      filt=filt,
                                                      encoding=encoding,
                                                      add_metadata=add_metadata,
                                                      verbose=verbose)
    boot_df = pandas.concat(boot_dfs)
    return boot_df


def resampling_filts(resample_caching_scheme, mp_folder, user_filt=None):
    """
    Function used to specify various way of caching resamples of analysis
    results.
    It is the responsibility of this function to ensure that all
    caching filters are consistent with user_filt.
    See apply_analysis below.
    TODO? Could add a scheme where caching is done by type of model.
    """
    caching_filts = []
    mp_files = [path.splitext(e)[0] for e in os.listdir(mp_folder)
                if path.splitext(e)[1] == '.pickle']
    if resample_caching_scheme == 'mp_file':
        for mp_fname in mp_files:
            # only use caching filters useful given user-provided filt
            if (user_filt is None) or user_filt(mp_fname):
                # use second arg default value to avoid scope issues 
                filt = lambda boot_mp_fname, mp_fname=mp_fname:\
                            mp_fname in boot_mp_fname
                caching_filts.append((mp_fname, filt))
    elif resample_caching_scheme == 'sametestset_mp_filepairs':
        # analysis not assumed symmetric, so we loop over all
        # pairs
        for mp_fname1 in mp_files:
            # only use caching filters useful given user-provided filt
            if user_filt(mp_fname1):
                metadata1 = dict(parse_res_fname(mp_fname1))
                for mp_fname2 in mp_files:
                    # only use caching filters useful given user-provided filt
                    if user_filt(mp_fname2):
                        metadata2 = dict(parse_res_fname(mp_fname2))
                        if metadata1['test set'] == metadata2['test set']:
                            filt_name = mp_fname1 + '___' + mp_fname2  # hacky
                            # use args default values to avoid scope issues
                            filt = lambda bname, n1=mp_fname1, n2=mp_fname2: \
                                    n1 in bname or n2 in bname
                            caching_filts.append((filt_name, filt))
    else:
        raise ValueError(('Unsupported resample caching scheme '
                          '{}'.format(resample_caching_scheme)))
    return caching_filts


def apply_analysis(analysis, mp_folder,
                   filt=None,
                   add_metadata=None,
                   resampling=False,
                   resample_caching_scheme=None,
                   analysis_folder=None,
                   pickle_encoding=None,
                   resampled_pickle_encoding="latin1",
                   verbose=0):
    """
    analysis: function that takes a pandas dataframe containing all
        required minimal-pair scores and returns the analysis results
        of interest (in a pandas dataframe if resampling=True).
    mp_folder: folder where the pickles containing minimal-pair scores are stored
        if resampling=True, mp_folder should also contain a 'resampling' subfolder
        where pickles containing resampled versions of the minimal-pair scores
        are stored.
    filt: string -> bool function, that takes the name of a file in mp_folder
        and returns True iff that file should be included in the analysis. If
        set to None, all available files are included.
    add_metadata: pandas.Dataframe -> pandas.Dataframe function, that takes a
        raw mp_scores Dataframe (containing only 'contrast', 'error' and primary
        metadata columns, where primary metadata is as specified in the
        config.yml file) and adds some additional metadata columns to it
    resampling: whether or not to use resampling. Currently, this is only
        supported for minimal pairs averaged on speaker first then on context.
        This returns the full bootstrapped data and also adds resampling-based
        standard deviation estimate to the analysis results.
    resample_caching_scheme: if resampling is True, determines whether and how
        to cache resampled analysis results. Caching results on disk is useful:
            - if applying the analysis on resamples takes too long (if there are
              N resamples, the duration required for the analysis will be
              multiplied by N compared to applying the analysis without
              resampling)
            - if loading resampled minimal pair scores at once for all relevant
              files in mp_folder (as determined by filt) exhausts the available
              memory
        Currently there is only three supported values for
        resample_caching_scheme:
            - None: no caching
            - 'mp_file': will create one cache file per (non-resampled)
               minimal-pair scores file.
              ** This should only be used for analyses which can be applied
                 independently for each set of minimal pair scores obtained
                 in the same ABX task with the same features
                 and dissimilarity function **
            - 'sametestset_mp_filepairs': will create one cache file
                per (ordered) pair of (non-resampled) minimal-pair scores
                files sharing the same test set.
              ** This should only be used for analyses comparing patterns of
                discriminability in the same ABX task for pairs of 
                (features/dissimilarity function couples). **
    analysis_folder: currently only used if resampling=True and
        resample_caching_scheme is not None, to specify where to store cached
        analysis resamples.
    pickle_encoding and resampled_pickle_encoding: useful to ensure pickles
        containing minimal pair scores, resp. resampled versions of those, will be
        read correctly, for example if they have been computed under a different 
        python environment than the current one.
    """
    if filt is None:
        filt = lambda mp_fname: True 
    df = fetch_data(analysis, mp_folder, filt=filt, encoding=pickle_encoding,
                    add_metadata=add_metadata)
    if resampling:
        boot_dfs = []
        resampled_mp_folder = path.join(mp_folder, 'resampling')
        if resample_caching_scheme is None:
            resampling_file = None
            boot_dfs.append(
                fetch_resampled_data(analysis, resampling_file,
                                     resampled_mp_folder,
                                     filt=filt,
                                     encoding=resampled_pickle_encoding,
                                     add_metadata=add_metadata,
                                     verbose=verbose))
        else:
            caching_filts = resampling_filts(resample_caching_scheme,
                                             mp_folder,
                                             user_filt=filt)
            assert not(analysis_folder is None)
            for filt_name, caching_filt in caching_filts:
                # keep and_filt in case we add other resampling caching schemes
                # where the caching filts are defined more coarsely than some
                # possible user-provided filters.
                and_filt = lambda mp_fname, f1=filt, f2=caching_filt:\
                                f1(mp_fname) and f2(mp_fname)
                resampling_file = path.join(analysis_folder,
                                            '{}.pickle'.format(filt_name))
                boot_dfs.append(
                    fetch_resampled_data(analysis, resampling_file,
                                         resampled_mp_folder,
                                         filt=and_filt,
                                         encoding=resampled_pickle_encoding,
                                         add_metadata=add_metadata,
                                         verbose=verbose))
        boot_df = pandas.concat(boot_dfs)
        # Add resulting standard deviation estimates to main dataframe 
        df = mp_scores.estimate_std(df, boot_df)
        # TODO: permutation tests
        return df, boot_df
    else:
        return df
