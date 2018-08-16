# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 12:06:47 2018

@author: Thomas Schatz

average error rates on C and V for the various corpora and models
"""



def plot_means(tasks, task_names, models, model_names, matched_lang, m, s, title=u"", filename=None):
    f, axes = plt.subplots(len(tasks), sharex=False, sharey=True, figsize=(15,40))
    for task, task_name, ax in zip(tasks, task_names, axes):
        m_t = 100.*(1.-np.array([m[task][model] for model in models]))
        # ad hoc ...
        models_bis = [e if e != 'input_feats' else 'input_features' for e in models]
        s_t = 100.*np.array([s[task][model] for model in models_bis])
        bar_list = ax.bar(np.arange(len(models)), m_t, linewidth=5, yerr=s_t, error_kw={'ecolor': 'k', 'capsize': 10})
        # default color: blue
        for bar in bar_list:
            bar.set_facecolor('w')
            bar.set_edgecolor('b')
        # matching lang in red
        for ix in matched_lang[task]:
            bar_list[ix].set_facecolor('w')
            bar_list[ix].set_edgecolor('r')
        # input-features in black (to be color-blind friendly)
        bar_list[-1].set_facecolor('w')
        bar_list[-1].set_edgecolor('k')
        ax.set_xticks(np.arange(len(models))+.4)
        texts = ax.set_xticklabels(model_names, fontsize=40)
        # default text color: blue
        for text in texts:
            text.set_color('b')
        #  red text for AE
        for ix in matched_lang[task]:
            texts[ix].set_color('r')
            #texts[ix].set_path_effects([path_effects.Stroke(linewidth=6,
            #                                                foreground='black'),
            #                            path_effects.Normal()])
        # black text for input features
        texts[-1].set_color('k')
        #ax.xaxis.labelpad = 40
        ax.set_ylabel("ABX error rate ($\%$)", fontsize=40)
        for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(40) 
        ax.set_xlim([-.2, len(tasks)+1])
        ax.set_ylim([0., 30.]) # for consistency with r/l and since we only care about a subset of the plots 35.])
        ax.yaxis.grid()
        ax.set_title(task_name, fontsize=50, y=1.05)#, x=.5, y=.6)
    plt.suptitle(title, fontsize=70)
    if not(filename is None):     
        plt.tight_layout()
        plt.subplots_adjust(top=0.9, hspace=.4)
        plt.savefig(filename)
        
        
corpora = ['WSJ', 'BUC', 'CSJ', 'GPM', 'GPV']
task_names = ['American English test stimuli (from WSJ)', 'American English test stimuli (from BUC)',
              'Japanese test stimuli (from CSJ)', 'Mandarin test stimuli (from GPM)', 'Vietnamese test stimuli (from GPV)']
models = ['WSJ', 'BUC', 'CSJ', 'GPM', 'GPV', 'input_feats']
model_names = ['WSJ\n(AE)', 'BUC\n(AE)', 'CSJ\n(Jap.)', 'GPM\n(Mand.)', 'GPV\n(Viet.)', 'Input feat.\n(Universal)']
matched_lang = {'WSJ': [0, 1], 'BUC': [0, 1], 'CSJ': [2], 'GPM': [3], 'GPV': [4]}

if model == 'HMM':
    target = '/Users/admin/Documents/PhD/Code/ABX_crossling/Results/figures'
else:
    target = '/Users/admin/Documents/PhD/Code/ABX_crossling/Results/figures_GMM'
fc = p.join(target, 'meanC_color.pdf')
fv = p.join(target, 'meanV_color.pdf')
plot_means(corpora, task_names, models, model_names, matched_lang, c_m, c_s, title=u"Consonants", filename=fc)
plot_means(corpora, task_names, models, model_names, matched_lang, v_m, v_s, title=u"Vowels", filename=fv)
#fc = p.join(target, 'meanC_HMMvsDPGMM.pdf')
#fv = p.join(target, 'meanV_HMMvsDPGMM.pdf')
#plot_means(['BUC', 'CSJ'],
#           ['American English (BUC)', 'Japanese (CSJ)'],
#           ['BUC', 'CSJ', 'input_feats'],
#           ['BUC', 'CSJ', 'Input features'],
#           {'BUC': [0], 'CSJ': [1]},
#           c_m, c_s, title=u"Consonants", filename=fc)
#plot_means(['BUC', 'CSJ'],
#           ['American English (BUC)', 'Japanese (CSJ)'],
#           ['BUC', 'CSJ', 'input_feats'],
#           ['BUC', 'CSJ', 'Input features'],
#           {'BUC': [0], 'CSJ': [1]},
#           v_m, v_s, title=u"Vowels", filename=fv)