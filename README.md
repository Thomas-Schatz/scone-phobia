# sconephobia README

## About

Perform analyses on results files obtained with the ABXpy library in a phone discrimination task BY (i.e. conditioned on) speaker and preceding and following contexts. (PHOne BY Speaker CONtext -> phobyscone -> sconephobia)

The only type of errors currently analysed are 'minimal-pair' discrimination errors obtained by symetrizing errors (i.e. averaging errors obtained when A and X are exemplars of phone_1 and B is an exemplar of phone_2 and when A and X are exemplars of phone_2 and B is an exemplar of phone_1) and then averaging them first on speaker and then on (preceding context, following context).

## Usage

  1. Install the library
    #TODO
      pip install ...
      Config? Download git, change config, install, or use directly from the git or change config in install location?
  2. Appropriately setup the ABXpy results files you want to analyse on your computer
    #TODO
  3. Run generic pre-computations
    #TODO
  4. Run existing analysis and plot scripts (located in the src/analyses and src/plots folder respectively) or read below on how to take advantage of the library to easily write (and contribute!) your own analysis and plot scripts. 


## Repo organisation

The idea is to have, on the one hand, a somewhat static set of general-purpose utilities that make it easy to write new analysis and plot scripts cleanly and easily and, on the other hand, an open-ended set of such analysis and plot scripts.

There are currently three packages (i.e. subfolders) in the src repository:
  - util: this is where general-purpose utilities are placed (read more about those below)
  - analyses: scripts for carrying out a particular analysis (e.g. comparing discrimination errors obtained with a Japanese vs an American English model on American English /r/-/l/ discrimination) should go there
  - plots: scripts used to generate plots from the results of a particular analysis should go there

## General-purpose utilities

This is the core part of the library, located in the src/util folder.

Content:

  - phonediscri_byspkcontext_mpscores: library core, not public?  -> mp_scores.py

      Functions for computing minimal pair scores from the results of ABX phone discrimination within speaker and context tasks.
      This assumes that the columns in the item file that was used to generate the ABX task are 'talker', 'prev-phone', 'next-phone' and 'contrast' although this would be easy to modify if needed.
  - Pre-computation scripts:
    - precompute_mp_scores: -> 
        command line interface calling phonediscri... to precompute mp-scores for all result files
in a specified folder
    - resample_mp_scores:
        command line interface calling phonediscr... to obtain boostrap resamples of ABX minimal-pair scores. Should be run in parallel on a cluster (can be long).
  - Script to access pre-computation results and apply analysis to it: analyze_mp_scores.py . sconephobia.apply_analysis(...)  
    ABXresults_management: depends on how mp-scores are computed and stored (as per precompute and resample?)
     - parse filenames of ABXpy results files and various kind of derived files to get info about content (not stored as meta data, directly in filename).
     - load pre-computed mp-scores in df
     - apply a particular analysis and put results in a df (is this the only public part? (get_results)) -> described proposed programming pattern


## Development

User contributions are welcome, especially to propose new analyses and plot scripts.

If you wish to contribute, first make your changes. Then run the following from the project root directory::

    source internal/test.sh

This will copy the template directory to a temporary directory, run the generation, then run tox. Any arguments passed will go directly to the tox command line, e.g.::

    source internal/test.sh -e py27

This command line would just test Python 2.7.


## Issues

Please report any bugs or requests that you have using the GitHub issue tracker!


## Authors

  - Thomas Schatz

## Acknowledgments

Based on the following python project template: https://github.com/seanfisk/python-project-template.
