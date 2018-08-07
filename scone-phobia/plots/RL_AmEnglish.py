# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 11:54:10 2018

@author: Thomas Schatz
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 10:43:32 2018

@author: Thomas Schatz

Plot figures related to American English (AE) /r/-/l/
"""



# To plot nice figures, uncomment the following and execute outside of spyder
# (use latex for text rendering in figure + unicode fonts)
# This requires to have the Doulos SIL font installed.
"""
import matplotlib as mpl
mpl.use("pgf")
pgf_with_custom_preamble = {
    "font.family": "serif", # use serif/main font for text elements
    "text.usetex": True,    # use inline math for ticks
    "pgf.rcfonts": False,   # don't setup fonts from rc parameters
    "pgf.preamble": [
         "\\usepackage{unicode-math}",  # unicode math setup
         "\\setmainfont{Doulos SIL}" # serif font via preamble
         ]
}
mpl.rcParams.update(pgf_with_custom_preamble)
"""


""" Quick test
import matplotlib.pyplot as plt
plt.figure(figsize=(4.5,2.5))
plt.plot(range(5))
#plt.xlabel(u"unicode text: я, ψ, €, ü, \\unitfrac[10]{°}{µm}")
#plt.ylabel(u"\\XeLaTeX")
plt.legend([u"unicode math: ɑ ɨi˧˩˧  ə̆ʊ˧˩˧"])
plt.tight_layout(.5)
plt.savefig('tt.pdf')
"""


import RL_AmEnglish
import matplotlib.pyplot as plt
import os.path as path
import numpy as np


data = RL_AmEnglish.get_results()

#TODO clean plotting code

##
# AE R/L
##

#TODO clean plotting code

def query_df(df, d):
    inds = [True]*len(df)
    for e in d:
        inds = (df[e] == d[e]) & inds
    return df[inds]

def plot_rl(task, models, contrasts, abx_errors, abx_errors_std,
            model_colors, contrasts_colors,
            task_label=None, model_labels=None, contrast_labels=None,
            out_file=None):
    # ABX errors expected in percent
    f, ax = plt.subplots(1, figsize=(13,5))
    if task_label is None:
        task_label = task
    if model_labels is None:
        model_labels = {model: model for model in models}
    if contrast_labels is None:
        contrast_labels = {contrast: contrast for contrast in contrasts}
    # order data dictionary content to list models' scores in right order
    order = lambda data, models: [data[model] for model in models]
    ordered_errs = {contrast: order(abx_errors[contrast], models)
                        for contrast in contrasts}
    ordered_stds = {contrast: order(abx_errors_std[contrast], models)
                        for contrast in contrasts}
    # space between 2 successive bars for given score
    stride = len(contrasts)+1
    bars = {}
    for i, contrast in enumerate(contrasts):
        # bar face (color indicates contrast)
        ax.bar(stride*np.arange(len(models))+i, ordered_errs[contrast],
               facecolor=contrast_colors[contrast], edgecolor=(0,0,0,0),
               linewidth=5, label=contrast_labels[contrast])
        # colored edges (colored later)
        bars[contrast] = ax.bar(stride*np.arange(len(models))+i,
                                ordered_errs[contrast],
                                facecolor=(1,1,1,0), edgecolor='k', linewidth=5,
                                label=None,
                                yerr=ordered_stds[contrast],
                                error_kw={'ecolor': 'k', 'capsize': 6,
                                       'linewidth': 2,
                                       'markeredgewidth': 2})     
    # set edge colors (color indicates language)
    for contrast in contrasts:
        b = bars[contrast]
        for i, model in enumerate(models):
            b[i].set_edgecolor(model_colors[model])
    # set x axis
    # x tick labels: model names with language color
    #FIXME it was 1.4 for 3, why???
    ax.set_xticks(stride*np.arange(len(models))+len(contrasts)/2.)
    ordered_model_labels = [model_labels[model] for model in models]
    texts = ax.set_xticklabels(ordered_model_labels, fontsize=24)
    for i, model in enumerate(models): 
        texts[i].set_color(model_colors[model])
    ax.set_xlim([-.2, stride*len(models)-1])
    ax.tick_params(axis='x', which='major', pad=10)
    # set y axis label and ticks
    ax.set_ylabel("ABX error rate ($\%$)", fontsize=27)
    for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(24) 
    ax.set_ylim([0., 35.])  #FIXME ad hoc?
    ax.yaxis.grid()
    ax.set_xlabel("Training set", fontsize=26)
    ax.set_title(task_label, fontsize=28, y=1.05)
    # legend (score types)
    plt.legend(fontsize=26, loc='upper left')
    if not(out_file is None):     
        plt.tight_layout()
        plt.savefig(out_file)


root = '/Users/admin/Documents/PhD/Code/perceptual-tuning-results/ABX/'  #HMMvsDNN/tri2vsnnet1/'
df_rl = data

# plot
model_types = ['AMtri2_sat_LMmono', 'AMnnet1_tri2_smbr_LMmono']
models = ['WSJ', 'BUC', 'GPJ', 'CSJ'] #['BUC', 'CSJ']  #
model_colors = {'WSJ': 'r', 'BUC': 'r', 'GPJ': 'b', 'CSJ': 'b'}  # by language
model_labels = {'WSJ': 'Read\n Am. English', 'BUC': 'Spont.\n Am. English',
                'GPJ': 'Read\n Japanese', 'CSJ': 'Spont.\n Japanese'}
#{'WSJ': 'WSJ (AE)', 'BUC': 'BUC (AE)',
#'GPJ': 'GPJ (Jap.)', 'CSJ': 'CSJ (Jap.)'}  #{'BUC': 'AE', 'CSJ': 'Japanese'}
contrasts = ['L-R', 'W-Y', 'all_C']
contrast2phones = {'L-R': ('R', 'L'), 'W-Y': ('W', 'Y')}
contrast_labels = {'L-R': '/ɹ/-/l/',
                   'W-Y': '/w/-/j/',
                   'all_C': 'average over consonant contrasts'}
contrast_colors = {'L-R': (0.9,0.9,0.9),
                   'W-Y': (0.45,0.45,0.45),
                   'all_C': (0,0,0)}
tasks = ['WSJ', 'BUC']  # ['WSJ'] 
task_labels = {'WSJ': '', #'American English test stimuli (from WSJ)',
               'BUC': ''} #'American English test stimuli (from BUC)'}
for model_type in model_types:
    for task in tasks:
        out_file = path.join(root, 'figures',
                             'RL_' + task + '_' + model_type + 'v3.pdf')
                             
                             
        ind_ty = df_rl['model type'] == model_type
        ind_ta = df_rl['test set'] == task
        dd = df_rl[ind_ty & ind_ta]
        abx_errors = {}
        abx_errors_std = {}
        for contrast in set(dd['contrast']):
            err = {}
            err_std = {}
            for model in set(dd['train set']):
                row = query_df(dd, {'train set': model, 
                                    'contrast': contrast})
                err[model] = row["error"].iloc[0]
                err_std[model] = row["std"].iloc[0]
            abx_errors[contrast] = err
            abx_errors_std[contrast] = err_std
    
        plot_rl(task, models, contrasts, abx_errors, abx_errors_std, 
                model_colors, contrast_colors,
                task_label=task_labels[task], model_labels=model_labels,
                contrast_labels=contrast_labels, out_file=out_file)