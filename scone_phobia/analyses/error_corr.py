# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 14:13:48 2018

@author: Thomas Schatz

This assumes:
  1. That the pandas.DataFrame specified as argument contains at least
     a'contrast', an 'error' and a 'test language' column.
  2. That scone_phobia.metadata.corpora specifies vowels and consonants for all
     corpora appearing in the 'test language' column.
  3. That an individual error pattern is obtained by grouping all lines
     sharing the same values in all columns but 'contrast' and 'error'.  
"""


# For each possible test corpus, for each possible pair of models tested
# on that corpus, get a cosine similarity.
    # could also get similarity for error patterns tested on two different corpora
    # of same language... Is that any good?

# Then can do different things, one being: for models defined independently 
# of test language, provided that they are tested on the same set of language,
# average the cosine similarity over those test languages.

# Another is: just focus on specific individual scores.


##
# error patterns cosine similarity
##

def get_corrs(df, models, tasks):
    groups = df.groupby(['task', 'model'])
    corrs= {}
    for task in tasks:
        corrs[task] = np.empty(shape=(len(models), len(models)))
        corrs[task][:,:] = np.nan
    for (task1, model1), df1 in groups:
       for (task2, model2), df2 in groups:
           if task1 == task2 and model1 != model2:
               i = models.index(model1)
               j = models.index(model2)
               df12 = pandas.merge(df1, df2, on=['p1', 'p2'], suffixes=['_1', '_2'])
               # convert to errors and normalize mean to 1
               err1 = 1.-df12['score_1']
               err2 = 1.-df12['score_2']
               err1 = err1/np.float(err1.mean())
               err2 = err2/np.float(err2.mean())
               corrs[task1][i, j] = np.dot(err1, err2)/(np.linalg.norm(err1)*np.linalg.norm(err2))  # np.corrcoef([err1, err2])[0,1]
    return corrs

if model == 'HMM':
    root = '/Users/admin/Documents/PhD/Code/ABX_crossling/Results/processed_data'
else:
    root = '/Users/admin/Documents/PhD/Code/ABX_crossling/Results/processed_data_GMM'
df_c = pandas.read_csv(p.join(root, 'C.csv'), sep='\t')
del df_c['Unnamed: 0']
df_v = pandas.read_csv(p.join(root, 'V.csv'), sep='\t')
del df_v['Unnamed: 0']

corpora = ['WSJ', 'BUC', 'CSJ', 'GPM', 'GPV']
task_names = ['American English (WSJ)', 'American English (BUC)',
              'Japanese (CSJ)', 'Mandarin (GPM)', 'Vietnamese (GPV)']
models = ['WSJ', 'BUC', 'CSJ', 'GPM', 'GPV', 'input_feats']
model_names = ['WSJ', 'BUC', 'CSJ', 'GPM', 'GPV', 'Input\nfeatures']

corr_c = get_corrs(df_c, models, corpora)
corr_v = get_corrs(df_v, models, corpora)

avg_c = np.zeros(shape=(len(models), len(models)))
avg_v = np.zeros(shape=(len(models), len(models)))
for task in corr_c:
    avg_c = avg_c + corr_c[task]
    avg_v = avg_v + corr_v[task]
avg_c = avg_c/np.float(len(corr_c))
avg_v = avg_v/np.float(len(corr_v))
# do not plot upper part as it is redundant
n = avg_c.shape[0]
for i in range(n):
    for j in range(i+1, n):
        avg_c[i, j] = np.nan
n = avg_v.shape[0]
for i in range(n):
    for j in range(i+1, n):
        avg_v[i, j] = np.nan    

if model == 'HMM':
    target = '/Users/admin/Documents/PhD/Code/ABX_crossling/Results/figures'
else:
    target = '/Users/admin/Documents/PhD/Code/ABX_crossling/Results/figures_GMM'
fc = p.join(target, 'corrC.pdf')
fv = p.join(target, 'corrV.pdf')
plot_cm(avg_c, model_names, fontsize=15, padding_x=20, padding_y=30, title='Consonants', scale=(0.85,1),
        filename=fc, title_fontsize=30, va='center', ha='center')
plot_cm(avg_v, model_names, fontsize=15, padding_x=20, padding_y=30, title='Vowels', scale=(0.85,1),
        filename=fv, title_fontsize=30, va='center', ha='center')
