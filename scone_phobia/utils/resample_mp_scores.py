# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 11:49:28 2018

@author: Thomas Schatz

Script to be ran in parallel on a cluster to obtain boostrap resamples of
ABX minimal-pair scores in a reasonable amount of time.

Usage: 
    python resample_mp_scores.py root model_type n_boot batch_id

batch_id is used both as a unique id for the output file and as a seed for 
random number generation.
"""

import scone_phobia.utils.mp_scores as mp_scores
import pickle
import os.path as path
import numpy as np


def resample_mp_scores(result_file, reg_cols, n_boot, batch_id):
    np.random.seed(batch_id)
    raw_res = mp_scores.load_df(result_file, reg_cols)
    mp_boot = mp_scores.resample_mp_score_within_speakers(raw_res, n_boot,
                                                          reg_cols)
    return mp_boot


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('result_file',
                        help="path to ABXpy result file (input)")
    parser.add_argument('output_folder',
                        help="folder where resample will be stored") 
    parser.add_argument('n_boot', type=int,
                        help="number of boostrap resampling to be computed")
    parser.add_argument('batch_id', type=int,
                        help="unique identifier for the result file")
    args = parser.parse_args()

    # hard-coded for now:
    reg_cols = ['talker', 'prev-phone', 'next-phone']
    fid = path.splitext(path.basename(args.result_file))[0]
    fname = fid + '__batchsize{}__batch{}.pickle'.format(args.n_boot,
                                                       args.batch_id)
    res_path = path.join(args.output_folder, fname)
    assert path.exists(args.result_file), args.result_file
    assert path.exists(args.output_folder), args.output_folder
    assert not(path.exists(res_path)), res_path

    mp_boot = resample_mp_scores(args.result_file, reg_cols,
                                 args.n_boot, args.batch_id)

    with open(res_path, 'wb') as fh:
        pickle.dump(mp_boot, fh)