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
                kwargs['cfg'] = yaml.load(ymlfile)['primary-metadata']
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
                matches.append((key, token))
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
def parse_bootres_fname(name, cfg=None):
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

def fetch_data(analysis, mp_folder, filt=None, encoding=None):
    """Use the above to get just the right data"""
    get_metadata = lambda x: parse_res_fname(x)
    df = mp_scores.load_mp_errors(mp_folder,
                                  get_metadata,
                                  filt=filt,
                                  encoding=encoding) # load all mp scores in a big df
    df = analysis(df)  
    return df


def fetch_resampled_data(analysis,
                         resampling_file,
                         resampled_mp_folder=None,
                         filt=None,
                         encoding=None):
    # Getting resampled minimal-pair scores to estimate variability.
    # This can take time so results are saved once they are computed
    get_metadata = lambda x: parse_bootres_fname(x)
    boot_dfs = mp_scores.resample_analysis_cached(resampling_file,
                                                  analysis,
                                                  resampled_mp_folder,
                                                  get_metadata,
                                                  encoding=encoding,
                                                  filt=filt)
    boot_df = pandas.concat(boot_dfs)
    return boot_df


# Organised with one resampling file per model-type here. Could be done
# with finer or larger granularity depending on needs. Be careful that 
# resampling file for whole model-type will need to be removed and recomputed
# if we add more train or test corpora or use different distances for example.
# Also could want to do resampling with more granularity if resampling are missing
# for some of the models.
def apply_analysis(analysis, mp_folder,
                   model_types, resampling=True, analysis_folder=None,
                   pickle_encoding=None, resampled_pickle_encoding="latin1"):
    """
    analysis: function that takes a pandas dataframe containing all
        required minimal-pair scores and returns the analysis results
        of interest (in a pandas dataframe if resampling=True).
    mp_folder: folder where the pickles containing minimal-pair scores are stored
        if resampling=True, mp_folder should also contain a 'resampling' subfolder
        where pickles containing resampled versions of the minimal-pair scores
        are stored.
    model_types: list of identifiers, such that only minimal-pair pickles containing
        at least one of the identifiers in their filename will be included in the 
        analysis. Should probably be modified if we stop relying on filenames for
        specifying primary metadata.
    resampling: whether or not to use resampling. Currently, this only adds
        resampling-based standard deviation estimate to the analysis results,
        but it would be easy to compute and other resampled quantities. E.g. pairwise
        permutation tests for differences in scores between two models.
    analysis_folder: currently only used if resampling=True to store analysis
        resamples (which can take some time to compute).
    pickle_encoding and resampled_pickle_encoding: useful to ensure pickles will be
    read correctly, for example if they have been computed under a different 
    python environment.
    """
    filt = lambda model: any([s in model for s in model_types])
    df = fetch_data(analysis, mp_folder, filt=filt, encoding=pickle_encoding)
    if resampling:
        resampled_mp_folder = path.join(mp_folder, 'resampling')
        boot_dfs = []
        for model_type in model_types:
            filt = lambda model: model_type in model
            resampling_file = path.join(analysis_folder,
                                        '{}.pickle'.format(model_type))
            boot_dfs.append(
                fetch_resampled_data(analysis, resampling_file,
                                     resampled_mp_folder,
                                     filt=filt, encoding=resampled_pickle_encoding))
        boot_df = pandas.concat(boot_dfs)
        # Add resulting standard deviation estimates to main dataframe 
        df = mp_scores.estimate_std(df, boot_df)
        # TODO: permutation tests
    return df
