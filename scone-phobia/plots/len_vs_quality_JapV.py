# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 10:43:32 2018

@author: Thomas Schatz

Plot figures related to vowel length contrasts in Japanese
"""



# To plot nice figures, uncomment the following and execute outside of spyder
# (use latex for text rendering in figure + unicode fonts)
# This requires to have the Doulos SIL font installed.
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


import len_vs_quality_JapV
import matplotlib.pyplot as plt
import os.path as path
import numpy as np


data = len_vs_quality_JapV.get_results()

#TODO clean plotting code

def query_df(df, d):
    inds = [True]*len(df)
    for e in d:
        inds = (df[e] == d[e]) & inds
    return df[inds]


def plot_dur(df_avg, root):
    for m_t, m in [('AMnnet1_tri2_smbr_LMmono', 'NN'),
                   ('AMtri2_sat_LMmono', 'HMM'),
                   ('dpgmm_vtln_vad', 'GMM'),
                   ('mfcc_vtln', 'VTLN MFCC')]:
        for test_set in ['CSJ', 'GPJ']:
            out_file = path.join(root, 'figures', m+"_"+test_set+"_durationv3.pdf")
            fig, axes = plt.subplots(nrows=1, ncols=2, sharey=True,
                                     figsize=(13, 5))
            for ctype, ax in zip(['length', 'quality'], axes):
                query = {"contrast type": ctype, "model type": m_t,
                         "test set": test_set}
                order = ['WSJ', 'BUC', 'GPJ', 'CSJ']
                model_names = ['Read\n Eng.', 'Spont.\n Eng.',
                               'Read\n Jap.', 'Spont.\n Jap.']
                y, yerr = [], []                
                for corpus in order:
                    query["train set"] = corpus
                    df = query_df(df_avg, query)
                    y.append(df["error"].iloc[0])
                    yerr.append(df["std"].iloc[0])
                bar = ax.bar(np.arange(len(y))+1, y, yerr=yerr,
                             error_kw={'ecolor': 'k', 'capsize': 6,
                                       'linewidth': 2,
                                       'markeredgewidth': 2})
                bar[0].set_facecolor((.8,0,0))
                bar[1].set_facecolor((.8,0,0))
                bar[2].set_facecolor((0,0,0.8))
                bar[3].set_facecolor((0,0,0.8))
                ax.set_xticks([1.4, 2.4, 3.4, 4.4])
                texts = ax.set_xticklabels(model_names, fontsize=24)
                texts[0].set_color((.8,0,0))
                texts[1].set_color((.8,0,0))
                texts[2].set_color((0,0,0.8))
                texts[3].set_color((0,0,0.8))
                ax.set_xlim([.8, 5])
                ax.set_xlabel("Training set", fontsize=26)
                ax.tick_params(axis='x', which='major', pad=10)
                # set y axis label and ticks
                if ctype=='length':
                    ax.set_ylabel("ABX error rate ($\%$)", fontsize=27)
                    ctypename = 'length'
                else:
                    ctypename = ctype
                for tick in ax.yaxis.get_major_ticks():
                        tick.label.set_fontsize(24) 
                ax.set_ylim([0., 35.])
                ax.yaxis.grid()
                ax.set_title("Vowel {} contrasts".format(ctypename),
                             fontsize=28, y=1.05)
            plt.tight_layout()
            plt.savefig(out_file)
    # legend            
    plt.figure()
    plt.bar([0, 1], [3, 1], color=(.8,0,0))
    plt.bar([2, 3], [1, 1], color=(0,0,0.8))
    plt.legend(['`Am. English native\' models', '`Japanese native\' models'], fontsize=18)
    plt.grid(None)
    plt.savefig(path.join(root, 'figures', "legend_durationv3.pdf"))


root = '/Users/admin/Documents/PhD/Code/perceptual-tuning-results/ABX/'  #HMMvsDNN/tri2vsnnet1/'
plot_dur(data, root)