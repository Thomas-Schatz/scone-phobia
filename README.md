# SCONE-PHOBIA

## About

Perform analyses on results files obtained with the [ABXpy library](https://github.com/bootphon/ABXpy) in a phone discrimination task BY (i.e. conditioned on) speaker and preceding and following contexts (PHOne BY Speaker CONtext -> phobyscone -> scone-phobia). See [Schatz et al. (2013)](http://thomas.schatz.cogserver.net/wp-content/uploads/2014/10/Schatz2013.pdf) and [Schatz (2016), PhD thesis](http://thomas.schatz.cogserver.net/wp-content/uploads/2016/10/Schatz2016.pdf) for background about machine ABX discrimination tasks.

This code can be used to analyze data from the OSF project https://osf.io/jpd74/ (discrimination of English and Japanese phonetic contrasts based on various models of speech processing trained either on English or Japanese).

The only type of errors currently analysed are 'minimal-pair' discrimination errors obtained by symetrizing errors (i.e. averaging errors obtained when A and X are exemplars of phone_1 and B is an exemplar of phone_2 and when A and X are exemplars of phone_2 and B is an exemplar of phone_1) and then averaging them first on speaker and then on (preceding context, following context).

## Tutorial

### Install the library
First clone the repository:
```
git clone git@github.com:Thomas-Schatz/scone-phobia.git
cd scone-phobia
```
Then create an appropriate config file. You can take inspiration from the [template config file](scone-phobia/config.yml.example) or use it directly by doing:
```
cp ./scone_phobia/config.yml.example ./scone_phobia/config.yml
```

Finally make sure that the `scone_phobia` module is on your PYTHONPATH (no actual install is needed, although an appropriate `setup.py` could easily be written if somebody wants a hard install):
```
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### Setup your data
Appropriately setup the ABXpy results files you want to analyze on your computer.

The main constraint is that the files should follow a naming scheme compatible with your config file, as described in [scone_phobia/utils/apply_analyses.py](scone_phobia/utils/apply_analyses.py) (The general idea is that the metadata for each file should be specified in the file name, or at least be deducible from it).

Here is an example compatible with the template config file, using the ABXpy results files from the https://osf.io/jpd74/ OSF project. You need to setup an OSF account, request access to the project and then download the example files (AMnnet1_tri2_smbr_LMmonomodel__BUCtrain__WSJtest__KLdis.txt and AMnnet1_tri2_smbr_LMmonomodel__CSJtrain__WSJtest__KLdis.txt) at https://osf.io/tgn9c/download and https://osf.io/d8uxn/download respectively.

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
Once minimal-pair scores have been computed (and optionally resampled), you can run existing [analysis scripts](scone_phobia/analyses) (depending on the nature of your data, not all scripts might be applicable, look at the comments within each script to check applicability conditions).

The [examples](./examples) folder contain examples of how to run analyses and plot the results under the form of [jupyter notebooks](https://jupyter.org/). They should work out of the box if you have completed the first parts of this tutorial. For example, to run the [RL_AmEnglish](./examples/RL_AmEnglish_example.ipynb) example, do:
```
cd ../examples
jupyter notebook
```
The jupyter notebook home will open in your internet browser. From there open the `RL_AmEnglish_example` notebook, select the first cell and run it (with shift+return) to get the analysis results under the form of a pandas DataFrame. Then run the second cell, to plot these results using the seaborn library. 

As you will see from the examples, performing an analysis boils down to calling the `apply_analysis` function from the [apply_analyses module](./scone_phobia/utils/apply_analyses.py) with appropriate arguments. Check the comments directly in the `apply_analysis` function definition for more information about available arguments and their utility.

### Writing (and contributing!) new analyses
To write your own analysis scripts, you can take inspiration from the [existing ones](scone_phobia/analyses). They are fairly simple pieces of code that take as input a pandas DataFrame containing a bunch of minimal-pair scores and output some analysis result. 

When developing new analyses, you might want to get an example of the DataFrame that will be passed as input to your analysis script. You can get one easily by calling the `fetch_data` function from the [apply_analyses module](./scone_phobia/utils/apply_analyses.py) with a "dummy" analysis that just returns its input. For example:
```
from scone_phobia.utils.apply_analyses import fetch_data
dummy = lambda x: x
df = fetch_data(analysis=dummy, mp_folder, filt, encoding, add_metadata))
```
where the `mp_folder`, `filt`, `encoding` and `add_metadata` arguments are the same you would pass to `apply_analysis` (the last three are optional).

Note that for your analysis to be compatible with the resampling mechanism (i.e. if you want to be able to obtain error bars for your analysis) its output should be under the form of a pandas DataFrame.

### Beyond minimal-pairs
TODO

## Repo organisation

There is, on the one hand, a somewhat static set of general-purpose utilities that makes it easy to write new analysis scripts and, on the other hand, an open-ended set of analysis scripts.

There are currently four packages (i.e. subfolders) in the repository:
  - `utils`: this is the core part of the library, where general-purpose utilities are placed
  - `metadata`: this is a place where metadata that is not directly stored in the ABXpy result filenames can be stored and made available to analysis scripts. Currently it contains only the `corpora.py` module which specifies the language, register, consonants and vowels for each corpus of speech recordings we have been using.
  - `analyses`: scripts for carrying out a particular analysis (e.g. comparing discrimination errors obtained with a Japanese vs an American English model on American English /r/-/l/ discrimination) should go there.
  - `plots`: any general-purpose plot utilities should go there.

## Development

User contributions are welcome, especially to propose new analysis scripts.


## Issues

Please report any bugs or requests that you have using the GitHub issue tracker!


## Authors

  - Thomas Schatz

## Acknowledgments

Modified from the following python project template: https://github.com/seanfisk/python-project-template.
