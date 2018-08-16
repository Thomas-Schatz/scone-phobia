# SCONE-PHOBIA

## About

Perform analyses on results files obtained with the [ABXpy library](https://github.com/bootphon/ABXpy) in a phone discrimination task BY (i.e. conditioned on) speaker and preceding and following contexts (PHOne BY Speaker CONtext -> phobyscone -> scone-phobia). See [Schatz et al. (2013)](http://thomas.schatz.cogserver.net/wp-content/uploads/2014/10/Schatz2013.pdf) and [Schatz (2016), PhD thesis](http://thomas.schatz.cogserver.net/wp-content/uploads/2016/10/Schatz2016.pdf) for background about machine ABX discrimination tasks.

This code can be used to analyze data from the OSF project https://osf.io/jpd74/ (discrimination of English and Japanese phonetic contrasts based on various models of speech processing trained either on English or Japanese).

The only type of errors currently analysed are 'minimal-pair' discrimination errors obtained by symetrizing errors (i.e. averaging errors obtained when A and X are exemplars of phone_1 and B is an exemplar of phone_2 and when A and X are exemplars of phone_2 and B is an exemplar of phone_1) and then averaging them first on speaker and then on (preceding context, following context).

## Usage tutorial

### Install the library
First clone the repository:
```
git clone git@github.com:Thomas-Schatz/scone-phobia.git
cd scone-phobia
```
Then create an appropriate config file. You can take inspiration from the [template config file](scone-phobia/config.yml.example) or use it directly by doing:
```
cp ./scone-phobia/config.yml.example ./scone-phobia/config.yml
```

Finally make sure that the `scone_phobia` module is on your PYTHONPATH (no actual install is needed, although an appropriate `setup.py` could easily be written if somebody wants a hard install):
```
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### Setup your data
Appropriately setup the ABXpy results files you want to analyze on your computer.

The main constraint is that the files should follow a naming scheme compatible with your config file, as described in [scone-phobia/utils/apply_analyses.py](scone-phobia/utils/apply_analyses.py) (The general idea is that the metadata for each file should be specified in the file name).

Here is an example compatible with the template config file, using theABXpy results files from the https://osf.io/jpd74/ OSF project. You need to setup an OSF account, request access to the project and then download the example files (AMnnet1_tri2_smbr_LMmonomodel__BUCtrain__WSJtest__KLdis.txt and AMnnet1_tri2_smbr_LMmonomodel__CSJtrain__WSJtest__KLdis.txt) at https://osf.io/qyrku/download and https://osf.io/9pwg2/download respectively.

Put these files in a directory of your choice, for example:
```
mkdir ../ABXpy_results
mv AMnnet1_tri2_smbr_LMmonomodel__BUCtrain__WSJtest__KLdis.txt ../ABXpy_results/
mv AMnnet1_tri2_smbr_LMmonomodel__CSJtrain__WSJtest__KLdis.txt ../ABXpy_results/
```

### Prepare minimal-pair scores
Computing minimal-pair discrimination errors can take a while, so we do it once and for all.

Using Python with appropriate libraries installed (see [requirements.txt](requirements.txt), the latest [python3-anaconda](https://www.anaconda.com/download/) should be more than enough for example), run:
```
cd scone_phobia
mkdir ../../mpscores
python utils/precompute_mp_scores.py ../../ABXpy_results ../../mpscores
```

### Resample minimal-pair scores (optional)
To get variability estimates for our analyses, we can resample minimal-pair scores. This can take a while so we do it only for n=4 boostrap resamples here. 

First we need to create a `resampling` subfolder in the folder where we put the minimal-pair scores:
```
mkdir ../../mpscores/resampling/
```
Then we call the resampling script for each ABXpy result file individually with two arguments numerical arguments. The first one indicates the number of resamples to be computed and the second one is used both as a random seed for the resampling and as a unique id for the resampled scores. This allows to easily split the computational burden of resampling into multiple independent jobs that can be run in parallel.

For example, one way to get our n=4 resamples is to compute n=2 resamples two times with random seeds 1 and 2 respectively:
```
python utils/resample_mp_scores.py ../../ABXpy_results/AMnnet1_tri2_smbr_LMmonomodel__BUCtrain__WSJtest__KLdis.txt ../../mpscores/resampling 2 1
python utils/resample_mp_scores.py ../../ABXpy_results/AMnnet1_tri2_smbr_LMmonomodel__BUCtrain__WSJtest__KLdis.txt ../../mpscores/resampling 2 2

python utils/resample_mp_scores.py ../../ABXpy_results/AMnnet1_tri2_smbr_LMmonomodel__CSJtrain__WSJtest__KLdis.txt ../../mpscores/resampling 2 1
python utils/resample_mp_scores.py ../../ABXpy_results/AMnnet1_tri2_smbr_LMmonomodel__CSJtrain__WSJtest__KLdis.txt ../../mpscores/resampling 2 2
```
Note that it is important for the validity of the results to use the same resampling scheme (number of resamples and random seeds) for each of the result files to be analyzed.

### Perform some analyses and plot the results
Once minimal-pair scores have been computed (and optionally resampled), you can run existing [analysis](scone-phobia/analyses) and [plot](scone-phobia/plots) scripts (depending on the nature of your data, not all scripts might be applicable, look at the comments within each script for applicability conditions). You can also take inspiration from the existing examples to write (and contribute!) your own analysis and plot scripts.

As an example, let us look at discrimination of American English /r/ and /l/ by American English-trained vs Japanese-trained models. If our models are [anything like humans](https://en.wikipedia.org/wiki/Perception_of_English_/r/_and_/l/_by_Japanese_speakers#Perception), Japanese-trained models should have a much harder time making this distinction than American English trained ones.

`AMnnet1_tri2_smbr_LMmonomodel__BUCtrain__WSJtest__KLdis.txt` contains discrimination scores for an Automatic Speech Recognition (ASR) system trained on the Buckeye corpus of American English and tested on the Wall Street Journal corpus of American English. `AMnnet1_tri2_smbr_LMmonomodel__CSJtrain__WSJtest__KLdis.txt` contains scores for the same ASR system tested on the same American English corpus, but trained on the Corpus of Spontaenous Japanese.

The [RL_AmEnglish](./scone-phobia/analyses/RL_AmEnglish.py) analysis can be applied to these results.
???:primary-metadata?
```
``` 

## Repo organisation

There is, on the one hand, a somewhat static set of general-purpose utilities that makes it easy to write new analysis and plot scripts and, on the other hand, an open-ended set of such analysis and plot scripts.

There are currently four packages (i.e. subfolders) in the repository:
  - `utils`: this is the core part of the library, where general-purpose utilities are placed
  - `metadata`: this is a place where metadata that is not directly stored in the ABXpy result filenames can be stored and made available to analysis and plot scripts. Currently it contains only the `corpora.py` module which specifies the language, register, consonants and vowels for each corpus of speech recordings we have been using.
  - `analyses`: scripts for carrying out a particular analysis (e.g. comparing discrimination errors obtained with a Japanese vs an American English model on American English /r/-/l/ discrimination) should go there
  - `plots`: scripts used to generate plots from the results of a particular analysis should go there

## Development

User contributions are welcome, especially to propose new analysis and plot scripts.


## Issues

Please report any bugs or requests that you have using the GitHub issue tracker!


## Authors

  - Thomas Schatz

## Acknowledgments

Modified from the following python project template: https://github.com/seanfisk/python-project-template.
