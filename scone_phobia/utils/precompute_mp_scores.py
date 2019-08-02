# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 17:05:31 2018

@author: Thomas Schatz

Command-line interface to precompute mp-scores for all result files
in a specified folder.

Usage example:
   cd path/2/ABX/results/folder/
   mkdir minimal_pair
   python precompute_mp_scores.py ./ minimal_pair
"""

import argparse
import os.path as path
import scone_phobia.utils.mp_scores as mp_scores


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_dir', help="ABX results files folder")
    parser.add_argument('out_dir', help="Folder where to store mp scores") 
    parser.add_argument('--overwrite', action='store_true',
                        help=("use this if you want to overwrite existing"
                              " pickles in out_dir"))
    parser.add_argument('--mp_type', default='spk_first',
                        help="Type of minimal-pair scores to compute")               
    args = parser.parse_args()
    assert path.exists(args.in_dir), \
        "Input folder {} missing".format(args.in_dir)
    assert path.exists(args.out_dir), \
        "Output folder {} missing".format(args.out_dir)
    if args.overwrite:
        filt = None
        print(("precompute_mp_scores.py: overwriting any pre-existing" 
               " pickle in {}".format(args.out_dir)))
    else:
        filt = lambda x: not(path.exists(path.join(args.out_dir, x+'.pickle')))
        print(("precompute_mp_scores.py: mp scores in pre-existing pickles"
               " in {} will not be computed again, use the --overwrite"
               " switch if you want to force them to be computed again."
               ).format(args.out_dir))
    mp_scores.precompute_mp_scores(args.in_dir, args.out_dir, filt=filt, mp_type=args.mp_type) 