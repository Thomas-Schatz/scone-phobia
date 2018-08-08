# SCONE-PHOBIA

## About

Perform analyses on results files obtained with the ABXpy library in a phone discrimination task BY (i.e. conditioned on) speaker and preceding and following contexts. (PHOne BY Speaker CONtext -> phobyscone -> scone-phobia)

This code can be used to analyze data from the OSF project https://osf.io/jpd74/ (discrimination of English and Japanese phonetic contrasts based on various models of speech processing trained either on English or Japanese).

The only type of errors currently analysed are 'minimal-pair' discrimination errors obtained by symetrizing errors (i.e. averaging errors obtained when A and X are exemplars of phone_1 and B is an exemplar of phone_2 and when A and X are exemplars of phone_2 and B is an exemplar of phone_1) and then averaging them first on speaker and then on (preceding context, following context).

## Usage tutorial

### Install the library
First clone the repository:
```
git clone git@github.com:Thomas-Schatz/scone-phobia.git
cd sconephobia
```
Then create an appropriate config file. You can take inspiration from the [template config file](scone-phobia/config.yml.example) or use it directly by doing:
```
cp ./sconephobia/config.yml.example ./sconephobia/config.yml
```

### Setup your data
Appropriately setup the ABXpy results files you want to analyse on your computer. Here is an example using an ABXpy results file from the https://osf.io/jpd74/ OSF project. You need to setup an OSF account, request access to the project then download the example files (AMnnet1_tri2_smbr_LMmonomodel__BUCtrain__BUCtest__KLdis.txt and AMnnet1_tri2_smbr_LMmonomodel__CSJtrain__BUCtest__KLdis.txt) at https://osf.io/qyrku/download and https://osf.io/9pwg2/download respectively.
Put these files in a directory of your choice, for example:
```
mkdir ../ABXpy_results
mv AMnnet1_tri2_smbr_LMmonomodel__BUCtrain__BUCtest__KLdis.txt ../ABXpy_results/
mv AMnnet1_tri2_smbr_LMmonomodel__CSJtrain__BUCtest__KLdis.txt ../ABXpy_results/
```

### Prepare minimal-pair scores
Computing minimal-pair discrimination errors can take a while, so we do it once and for all.
Using Python with appropriate libraries installed (see [requirements.txt](requirements.txt), the latest [python3-anaconda](https://www.anaconda.com/download/) should be more than enough for example), run:
```
cd scone-phobia
python utils/precompute_mp_scores.py ...
```
To get variability estimates for our analyses, we can resample minimal-pair scores. This can take a while so we do it only for n=2 boostrap resamples here. For real-world use cases, you'd want to call [scone-phobia/utils/resample_mp_scores.py](scone-phobia/utils/resample_mp_scores.py) in parallel on a cluster for many different choice of xxx, and then copy the results files back to your xxx/resampling folder.

### Perform some analyses and plot the results
Once minimal-pair scores have been computed (and optionally resampled), you can run existing analysis and plot scripts (located in the [scone-phobia/analyses](scone-phobia/analyses) and [scone-phobia/plots](scone-phobia/plots) folder respectively) or take inspiration from those scripts to write (and contribute!) your own analysis and plot scripts.

For more about the organisation of the library and how to contribute, read below. 


## Repo organisation

The idea is to have, on the one hand, a somewhat static set of general-purpose utilities that make it easy to write new analysis and plot scripts cleanly and easily and, on the other hand, an open-ended set of such analysis and plot scripts.

There are currently three packages (i.e. subfolders) in the src repository:
  - utils: this is where general-purpose utilities are placed (read more about those below)
  - analyses: scripts for carrying out a particular analysis (e.g. comparing discrimination errors obtained with a Japanese vs an American English model on American English /r/-/l/ discrimination) should go there
  - plots: scripts used to generate plots from the results of a particular analysis should go there

### General-purpose utilities

This is the core part of the library, located in the src/utils folder.

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
     - can use shared info about corpora (language, register, phone properties, etc.)

## Development

User contributions are welcome, especially to propose new analysis and plot scripts.


## Issues

Please report any bugs or requests that you have using the GitHub issue tracker!


## Authors

  - Thomas Schatz

## Acknowledgments

Based on the following python project template: https://github.com/seanfisk/python-project-template.
