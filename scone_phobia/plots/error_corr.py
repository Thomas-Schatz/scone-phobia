# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 14:12:25 2018

@author: Thomas Schatz
"""

# use latex for text rendering in figure + unicode fonts
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


import matplotlib.patheffects as path_effects
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import MDS


def fitMDS(dissimilarities, r):
    mds = MDS(metric=False, n_init=10000, random_state=r,
              dissimilarity='precomputed')
    mds.fit(dissimilarities)
    return mds.embedding_, mds.stress_  # embedding: n_models x 2 array


def plotEmbedding(embedding, labels, colors, title, filename=None):
    fig = plt.figure(frameon=False)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_aspect('equal', adjustable='box')
    # major ticks every .2, minor ticks every .05                                      
    major_ticks = np.arange(-1., 1.01, .2)                                              
    minor_ticks = np.arange(-1., 1.01, .05)                                               
    ax.set_xticks(major_ticks)                                                       
    ax.set_xticks(minor_ticks, minor=True)                                           
    ax.set_yticks(major_ticks)                                                       
    ax.set_yticks(minor_ticks, minor=True)                                           
    ax.grid(which='minor', alpha=0.2)                                                
    ax.grid(which='major', alpha=0.5) 
    for i, (lab, c) in enumerate(zip(labels, colors)):
        x, y = embedding[i,:]
        #plt.plot(x, y, 'x'+c, markersize=10)
        #plt.annotate(lab, xy=(x,y), xytext=(0, 10),
        #             textcoords='offset points', color=c,
        #             size=13, ha='center')
        ax.text(x, y, lab, ha="center", va="center", size=26, color=c)
    mx, Mx = min(embedding[:,0]), max(embedding[:,0])
    my, My = min(embedding[:,1]), max(embedding[:,1])
    mx, Mx = mx-.1, Mx+.1
    my, My = my-.05, My+.05
    ax.axis([mx, Mx, my, My])
    #plt.axis('off')
    ax.set_title(title, size=32)
    ax.title.set_position([.5, 1.02])
    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])
    if not(filename is None):
       plt.tight_layout()
       plt.savefig(filename)
       

def getFigDim(embedding):
    mx, Mx = min(embedding[:,0]), max(embedding[:,0])
    my, My = min(embedding[:,1]), max(embedding[:,1])
    mx, Mx = mx-.1, Mx+.1
    my, My = my-.05, My+.05
    return -1, 1, -.75, .75  #mx, Mx, my, My

def plot2Embeddings(embeddings, labels, colors, outline,
                    titles, filename=None):
    # we want two subplots with same aspect ratio, same scale,
    # but different absolute sizes
    mx1, Mx1, _, _ = getFigDim(embeddings[0])
    mx2, Mx2, _, _ = getFigDim(embeddings[1])
    r =  np.float(Mx2-mx2)/np.float(Mx1-mx1)
    fig, axes = plt.subplots(1, 2,
                             gridspec_kw = {'width_ratios':[1, r]},
                             frameon=False)
    for ax, embedding, title in zip(axes, embeddings, titles):
        ax.set_aspect('equal', adjustable='box')
        # major ticks every .2, minor ticks every .05                                      
        major_ticks = np.arange(-1., 1.01, .5)                                              
        minor_ticks = np.arange(-1., 1.01, .1)                                               
        ax.set_xticks(major_ticks)                                                       
        ax.set_xticks(minor_ticks, minor=True)                                           
        ax.set_yticks(major_ticks)                                                       
        ax.set_yticks(minor_ticks, minor=True)                                           
        ax.grid(which='minor', alpha=0.2)                                                
        ax.grid(which='major', alpha=0.5) 
        for i, (lab, c, ol) in enumerate(zip(labels,
                                             colors, 
                                             outline)):
            x, y = embedding[i,:]
            #plt.plot(x, y, 'x'+c, markersize=10)
            #plt.annotate(lab, xy=(x,y), xytext=(0, 10),
            #             textcoords='offset points', color=c,
            #             size=13, ha='center')
            text = ax.text(x, y, lab, ha="center", va="center",
                           size=20, color=c)
            if ol:
              text.set_path_effects([path_effects.Stroke(linewidth=3,
                                                         foreground='black'),
                                     path_effects.Normal()])
        figdim = getFigDim(embedding)
        ax.axis(figdim)
        #plt.axis('off')
        ax.set_title(title, size=22)
        ax.title.set_position([.5, 1.02])
        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])
        if not(filename is None):
           plt.tight_layout()
           plt.savefig(filename)

# correlation between average error patterns over 5 corpora (4 languages)
models = ['WSJ', 'BUC', 'CSJ', 'GPM', 'GPV', 'Input feat.']
#colors = ['r', 'r', 'c', 'b', 'k', 'g']
colors = ['r', 'r', 'b', 'b', 'b', 'k']  # 0.5 = gray
outline = [False, False, False, False, False, False]

corrC = [[1., .96, .937, .915, .896, .942],
         [.96, 1., .939, .914, .903, .941],
         [.937, .939, 1., .926, .906, .942],
         [.915, .914, .926, 1., .924, .917],
         [.896, .903, .906, .924, 1., .916],
         [.942, .941, .942, .917, .916, 1.]]
corrV = [[1., .936, .896, .883, .875, .914],
         [.936, 1., .903, .894, .882, .924],
         [.896, .903, 1., .867, .852, .899],
         [.883, .894, .867, 1., .883, .892],
         [.875, .882, .852, .883, 1., .887],
         [.914, .924, .899, .892, .887, 1.]]



dissC = 1. - np.array(corrC)
dissV = 1. - np.array(corrV)


"""
for r in range(10):  # random initial state
    embC, stressC = fitMDS(dissC, r)
    embV, stressV = fitMDS(dissV, r)    
    plotEmbedding(embC, models, colors,  'Consonants',
                  'corrCmds{0}_stress{1:.5f}.pdf'.format(r, stressC))
    plotEmbedding(embV, models, colors, 'Vowels',
                  'corrVmds{0}_stress{1:.5f}.pdf'.format(r, stressV))
""" 
"""             
# after testing with 10000 init, random seed 0 for consonants and 5 for vowels
# gave the embeddings with the lowest stress
rC = 0
rV = 5
embC, stressC = fitMDS(dissC, rC)
embV, stressV = fitMDS(dissV, rV)
np.save('corrCembedding', embC)
np.save('corrVembedding', embV)
"""
embC = np.load('corrCembedding.npy')
embV = np.load('corrVembedding.npy')
#plotEmbedding(embC, models, colors,  'Consonants',
#              'corrCmds.pdf')
#plotEmbedding(embV, models, colors, 'Vowels',
#              'corrVmds.pdf')
plot2Embeddings([embC, embV], models, colors, outline, ['Consonants', 'Vowels'],
               'corrCVmds_color.pdf')