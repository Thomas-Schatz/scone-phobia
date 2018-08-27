# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 14:12:25 2018

@author: Thomas Schatz

Plots for perceptual tuning paper.
"""

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


import numpy as np
from sklearn.manifold import smacof
import matplotlib.pyplot as plt
# this is necessary for 3D plots even if not used explicitly
import mpl_toolkits.mplot3d

def select_test_sets(df, test_sets):
    """
    Should be applied to df obtained from scone_phobia.analyses.error_sim.
    """
    ind = np.array([e in test_sets for e in df['test set']])
    df = df[ind]
    return df


def avg_sim(df):
    """
    Should be applied to df obtained from scone_phobia.analyses.error_sim.
    Averages similarity obtained on different test sets for each model, where
    a model is obtained as combination of model type, training language and
    training register.
    """
    avg_df = df.groupby(['model type A', 'model type B',
                         'training language A', 'training language B',
                         'training register A', 'training register B'],
                         as_index=False).mean()
    return avg_df


def get_dis_df(m1, m2, df):
    # utility function for get_sim_matrix
    t1, r1, l1 = m1
    t2, r2, l2 = m2
    res = df[(df['model type A'] == t1) &\
             (df['model type B'] == t2) &\
             (df['training language A'] == l1) &\
             (df['training language B'] == l2) &\
             (df['training register A'] == r1) &\
             (df['training register B'] == r2)]
    assert len(res) == 1, (df, m1, m2)
    # this works because the similarities are angular distances!
    return 1-res['err_sim']             


def get_dis_emb(m1, m2, data):
    # utility function for get_sim_matrix
    models, emb = data
    euclidean_d = lambda x, y: np.linalg.norm(x-y)
    d = euclidean_d(emb[models.index(m1),:], emb[models.index(m2),:])
    return d

           
def get_dis_matrix(models, data, get_dis):
    """
    Get matrix of dissimilarities for the given models,
    where models are given as a list of triplets
    indicating (model type, training register, training language)
    """            
    diss = np.zeros(shape=(len(models), len(models)))
    for i1, m1 in enumerate(models):
        for i2, m2 in enumerate(models):
            dis = get_dis(m1, m2, data)
            diss[i1, i2] = dis
    return diss


def get_dis_corr(dis_mat1, dis_mat2):
    # compute correlation between dissimilarities in two matrices
    # of dissimilarities
    c = np.corrcoef([f for e in dis_mat1 for f in e],
                    [f for e in dis_mat2 for f in e])[0, 1]
    return c


def get_embedding(df, models, test_sets, emb_dim=2):
    """
    Get an embedding for 'models' provided as (model type, training register,
    training language) triplets, where the dissimilarities that the embedding
    attempts to fit are obtained by averaging over dissimilarities obtained
    for each of the specified 'test_sets'.
    """
    df = select_test_sets(df, test_sets)
    df = avg_sim(df)
    dis_matrix = get_dis_matrix(models, df, get_dis_df)
    # get embedding from scikit-learn smacof
    emb, stress = smacof(dis_matrix, metric=True, n_init=1000,
                         random_state=0, init=None, n_components=emb_dim)
    # get embedding distances
    dis_matrix_emb = get_dis_matrix(models, (models, emb), get_dis_emb)
    dis_corr = get_dis_corr(dis_matrix, dis_matrix_emb)
    return emb, stress, dis_corr


def fig1_stress(df, filename=None):
    test_sets = ['WSJ', 'GPJ']
    models = [ ('dpgmm_vtln_vad',
                'Spontaneous', 'American English'),
               ('dpgmm_vtln_vad',
                'Spontaneous', 'Japanese'),
               ('AMtri1_sat_small_LMtri1satsmall',
                'Spontaneous', 'American English'),
               ('AMtri1_sat_small_LMtri1satsmall',
                'Spontaneous', 'Japanese'),
               ('mfcc_novtln',
                'None', 'None') ]
    stresses = []  # we could also look at corrs, but I wonder if in SMACOF
                   # the two are not formally related anyway
    dims = range(1, 10)
    for d in dims:
        _, stress, _ = get_embedding(df, models, test_sets, emb_dim=d)
        stresses.append(stress)
    fig = plt.figure(frameon=False, )
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(dims, stresses, 'o-')
    if not(filename is None):
       plt.tight_layout()
       plt.savefig(filename)


def fig1_sim3D(df, filename=None, azim=0., elev=0., dotted_edges=None): 
    """
    Custom 3d plot with 2 unsupervised model resp. trained on Jap. and AE
    spontaneous, 2 matching supervised baseline and an input features baseline.
    Based on similarities averaged over the two read test sets.
    
    Edges drawn between input features and all others and between models sharing
    either model type or training language.
    
    Marker color indicates training language.
    Marker type indicates model type.
    """
    if dotted_edges is None:
        dotted_edges = []
    test_sets = ['WSJ', 'GPJ']
    models = [ ('dpgmm_vtln_vad',
                'Spontaneous', 'American English'),
               ('dpgmm_vtln_vad',
                'Spontaneous', 'Japanese'),
               ('AMtri1_sat_small_LMtri1satsmall',
                'Spontaneous', 'American English'),
               ('AMtri1_sat_small_LMtri1satsmall',
                'Spontaneous', 'Japanese'),
               ('mfcc_novtln',
                'None', 'None') ]
    markers = ['*', '*', 's', 's', 'o']
    colors = ['r', 'b', 'r', 'b', 'y']
    marker_sizes = [14, 14, 10, 10, 10]
    edges = [(0, 4), (1, 4), (2, 4), (3, 4), (0, 1), (2, 3), (0, 2), (1, 3)]
    emb, stress, dis_corr = get_embedding(df, models, test_sets, emb_dim=3)
    # the following part could be in a shared auxiliary function maybe?
    fig = plt.figure(frameon=False)
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    ax.set_aspect('equal', adjustable='box')
    for i, (a, b) in enumerate(edges):
        if i in dotted_edges:
            # should do a function for this messy bit
            dot_length=.01  # ad hoc...
            edge_sty = '-k'
            xa, ya, za = emb[a,:]
            xb, yb, zb = emb[b,:]
            d_ab = np.linalg.norm(emb[a,:]-emb[b,:])
            nb_spaces = np.int(np.floor(d_ab/dot_length))
            nb_dots = np.int(np.ceil(nb_spaces/2.))
            last_dot = (nb_spaces % 2 == 0)
            if last_dot:
                last_dot_len = d_ab-dot_length*nb_spaces
            xb_c = xa + (xb-xa)*(2.*nb_dots-1.)*dot_length/d_ab
            yb_c = ya + (yb-ya)*(2.*nb_dots-1.)*dot_length/d_ab
            zb_c = za + (zb-za)*(2.*nb_dots-1.)*dot_length/d_ab
            xs = np.linspace(xa, xb_c, nb_dots)
            ys = np.linspace(ya, yb_c, nb_dots)
            zs = np.linspace(za, zb_c, nb_dots)
            for x1, y1, z1, x2, y2, z2 in zip(xs[::2], ys[::2], zs[::2],
                                              xs[1::2], ys[1::2], zs[1::2]): 
                
                ax.plot([x1, x2], [y1, y2], [z1, z2], edge_sty)
            if last_dot:
                x1 = xb + (xa-xb)*last_dot_len/d_ab
                y1 = yb + (ya-yb)*last_dot_len/d_ab
                z1 = zb + (za-zb)*last_dot_len/d_ab
                x2, y2, z2 = xb, yb, zb
                ax.plot([x1, x2], [y1, y2], [z1, z2], edge_sty)
        else:
            edge_sty = '-k'
            xa, ya, za = emb[a,:]
            xb, yb, zb = emb[b,:]
            ax.plot([xa, xb], [ya, yb], [za, zb], edge_sty)
    for i in range(len(models)):
        x, y, z = emb[i,:]
        ax.plot([x], [y], [z],
                marker=markers[i],
                color=colors[i],
                markersize=marker_sizes[i])
    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])
    ax.zaxis.set_ticklabels([])
    plt.axis('off')
    ax.view_init(azim=azim, elev=elev)
    if not(filename is None):
       plt.tight_layout()
       plt.savefig(filename)
