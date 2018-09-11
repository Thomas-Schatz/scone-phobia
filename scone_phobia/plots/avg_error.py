# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 12:06:47 2018

@author: Thomas Schatz

Generic bar plot function for data with three levels of hierarchy
as defined by a 3 column dataframe.

TODO: should cut this into smaller better documented functions...


level3_bar_aux([[[1, 2, 3],
                 [2, 2, 2]],
                 [[1, 2, 3],
                 [2, 2, 3]]],
               error_bars=[[[.1, .5, .1],
                            [.1, .5, .1]],
                           [[.1, .5, .1],
                            [.1, .5, .1]]],
               face_colors=[[[(1, 1, .8, 1), (1, .9, .9, 1),(.85, .95, 1, 1)],
                             [(1, 1, .8, 1), (1, .9, .9, 1),(.85, .95, 1, 1)]],
                            [[(1, 1, .8, 1), (1, .9, .9, 1),(.85, .95, 1, 1)],
                             [(1, 1, .8, 1), (1, .9, .9, 1),(.85, .95, 1, 1)]]],
               edge_colors=[[['y','y','y'],
                             ['y','y','y']],
                            [['r','r','r'],
                             ['r','r','r']]],
               l1_labels = [[['x', 'y', 'z'],
                             ['x', 'y', 'z']],
                            [['x', 'y', 'z'],
                             ['x', 'y', 'z']]],
               l2_labels = [['AE', 'Jap.'],
                            ['AE', 'Jap.']],
               l3_labels = ['Unsup.', 'Sup.'],
               title="Test!")

level3_bar_aux([[[1, 1, 1, 1]], [[2, 2, 1, 1]], [[3, 3, 1, 1]], [[4, 4, 1, 1, 6, 7]]],
               error_bars=[[[.1, .1, .1, .1]], [[.3, .1, .1, .1]], [[.1, .1, .1, .1]], [[.1, .1, .1, .1, .1, .1]]],
               face_colors=[[['k', 'k', 'k', 'k']], [['k', 'k', 'k', 'k']], [['k', 'k', 'r', 'r']], [['k', 'k', 'r', 'r', 'r', 'r']]],
               edge_colors=[[['k', 'k', 'k', 'k']], [['k', 'k', 'k', 'k']], [['k', 'k', 'r', 'r']], [['k', 'k', 'r', 'r', 'r', 'r']]],
               l1_labels = None,
               l2_labels = None,
               l3_labels = ['Unsup.', 'Sup.', 'RR', 'VV'],
               title="Test!")

"""




import numpy as np
import matplotlib.pyplot as plt
import numbers



def agg_x_intervals(x_left, x_right, grp_spacing, nb_level, agg_l, agg_r):
    # aux function for get_x
    l_list, r_list = [], []
    offset = 0
    for l, r in zip(x_left, x_right):
        l_list.append(agg_l(l) + offset)
        r_list.append(agg_r(r) + offset)
        # linear increase of group spacing with group level
        offset = offset + r[-1] + grp_spacing*nb_level
    xl, xr = np.concatenate(l_list), np.concatenate(r_list)
    return xl, xr


def get_x(data, agg_level, bar_width=.8):
    """
    Get group abscissas for specified level.
    
    agg_level: specifies for which group level, in the hierarchy specified
               by data, we want the abscissas (1  for the most detailed level,
               2 for next most detailed, etc.)
    
    Bar spacing is .2, group spacing is 1 for level 1 boundaries, 2 for level 2
    etc. Bar width is up to the user.
    
    Returns left and right abscissas for groups at level specified as well
    as total number of levels found in data.
    """
    assert data, "Empty data"
    bar_spacing = .2
    grp_spacing = 1
    if isinstance(data[0], numbers.Number):
        # base case
        x, nb_level = (bar_width+bar_spacing)*np.arange(len(data)), 1
        xl, xr = x, x+bar_width
    else:
        # recursion
        args = [agg_level]
        kwargs = {'bar_width': bar_width, 'x_type': 'interval'}
        xl, xr, nb_levels = zip(*[get_x(e, *args, **kwargs) for e in data])
        # check data is correctly formatted
        assert all([e == nb_levels[0] for e in nb_levels])
        # aggregate abscissas
        nb_level = nb_levels[0] + 1
        if nb_level == agg_level:
            agg_l, agg_r = (lambda x: np.array([x[0]])), (lambda x: np.array([x[-1]]))
        else:
            agg_l, agg_r = (lambda x: x), (lambda x: x)
        xl, xr = agg_x_intervals(xl, xr, grp_spacing, nb_level, agg_l, agg_r)                 
    return xl, xr, nb_level
   

def axis2points(ax, x):
    xmi, xma = ax.get_xlim()
    xmip, xmap = ax.get_window_extent().get_points()[:,0]
    return x/(xma-xmi)*(xmap-xmip)



def get_l3widths(data):
    offset = 1
    # detect if there is only two levels
    two_levels = all([len(f) == 1 for e in data for f in e])
    if two_levels:
        offset_increment = 0
    else:
        offset_increment = 1
    l3widths = []
    for e in data:
        start, stop = [], []
        for f in e:
            start.append(offset)
            stop.append(offset + len(f) - .2)
            offset = offset + len(f) + offset_increment
        l3widths.append(stop[-1] - start[0])
        offset = offset + 1
    return l3widths


def grouped_bar_(data, nb_levels, error_bars=None, face_colors=None, edge_colors=None,
                   title=None, figsize=None, group_labels=None,
                   label_style=None, bar_width=.8,
                   l1_labels=None, l2_labels=None,
                   l3_labels=None, l3_addlines=None,
                   ylab=None, ylab_fontsize=27, yrange=None,
                   out_file=None):
    """
    Low-level function plotting bars grouped in a tree-like hierarchy.   
    Space is left between bars at boundaries between hierarchy levels
    with the amount of space increasing with level.

    data: nested list of floats. For example for a 2 level hierarchy
          data would be a ((float list) list)
    """
        
    
    # create fig
    if figsize is None:
        figsize = (2*sum([len(f) for e in data for f in e]), 5)
    f, ax = plt.subplots(1, figsize=figsize)
    # get flat data list and corresponding abscissa
    y = [g for e in data for f in e for g in f]
    x = get_abscissa(data)
    # plot colored faces of bars one by one (optional)
    # do it first to get it as background
    if not(face_colors is None):
        fcolors = [g for e in face_colors for f in e for g in f]
        for xx, yy, c in zip(x, y, fcolors):
            ax.bar([xx], [yy],
                   linewidth=5,
                   edgecolor=(0,0,0,0),
                   facecolor=c)
    # add uncolored edges + optional error bars
    if not(error_bars is None):
        yerr=[g for e in error_bars for f in e for g in f]
    else:
        yerr=None
    edge_bars = ax.bar(x, y,
                       linewidth=5,
                       facecolor=(1,1,1,0),
                       edgecolor='k', 
                       yerr=yerr,
                       error_kw={'ecolor': 'k', 'capsize': 6,
                                 'linewidth': 2,
                                 'markeredgewidth': 2})
    # set edge colors (optional)
    if not(edge_colors is None):
        ecolors = [g for e in edge_colors for f in e for g in f]
        for bar, color in zip(edge_bars, ecolors):
            bar.set_edgecolor(color)
    # set x axis labels (up to 3 layers)
    tickfs = 24  # fontsize
    x1, x2, x3 = [], [], []
    y1, y2, y3 = 0, 0, 0
    l1, l2, l3 = [], [], []
    if not(l1_labels is None):
        x1 = get_abscissa(data, level=1, bar_centers=True)
        l1 = [g for e in l1_labels for f in e for g in f]
        assert len(x1) == len(l1), (x1, l1)
        y2, y3 = y2+1, y3+1
    if not(l2_labels is None):
        x2 = get_abscissa(data, level=2, bar_centers=True)
        l2 = [f for e in l2_labels for f in e ]
        assert len(x2) == len(l2), (x2, l2)
        y3 = y3+1
    if l3_addlines is None:
        l3_addlines = [True]*len(l3_labels)
    if not(l3_labels is None):
        x3 = get_abscissa(data, level=3, bar_centers=True)
        l3_widths = get_l3widths(data)
        l3 = [add_line(ax, l, w, tickfs) if t else ('\n' + l)
                for l, w, t in zip(l3_labels, l3_widths, l3_addlines)]
        assert len(x3) == len(l3), (x3, l3)
    all_x = np.array(list(x1)+list(x2)+list(x3))
    y3 = y3+3 #FIXME ad hoc
    all_l = np.array(['\n'*yl + lab
                        for yl, l in zip([y1, y2, y3], [l1, l2, l3])
                            for lab in l])
    x_order = np.argsort(all_x)
    xticks = all_x[x_order]
    xticklabels = all_l[x_order]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, fontsize=tickfs)
    # if we add a tick color option: do
    # texts = ax.set_xticklabels(...)
    # for i, model in enumerate(models): 
    #    texts[i].set_color(model_colors[model])
    ax.set_xlim([.8, x[-1]+1])  # .8 bar width...
    ax.tick_params(axis='x', which='major', pad=10)  
    # set title (optional)
    if not(title is None):
        ax.set_title(title, fontsize=28, y=1.05)
    # set y axis
    if not(ylab is None):
        ax.set_ylabel(ylab, fontsize=ylab_fontsize)
    for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(24)
    if not(yrange is None):
        ax.set_ylim(yrange)
    ax.yaxis.grid()
    if not(out_file is None):     
        plt.tight_layout()
        plt.savefig(out_file)


def add_line(ax, lab, line_width, fontsize):
    # I think the line is too short for small
    # groups and too wide for large groups...
    # line_width computation seems correct, so maybe axis2points is bad?
    points = axis2points(ax, line_width)
    n = int(np.floor(points/fontsize))
    return '__'*n + '\n' + lab


def query_df(df, d):
    inds = [True]*len(df)
    for e in d:
        inds = (df[e] == d[e]) & inds
    return df[inds]


def level3_bar(df, data_col,
               c1, c2=None, c3=None,
               order_c1=None, order_c2=None, order_c3=None,
               errorbar_col=None, l3_addlines=None,
               labn1=None, labn2=None, labn3=None,
               
               **kwargs):
    """ main function """
    assert data_col in df, data_col
    assert c1 in df, c1
    if c2:
        assert c2 in df, c2
    if c3:
        assert c2
        assert c3 in df, c3
    if (order_c1 is None):
        order_c1 = list(np.unique(df[c1]))
    if c2 and (order_c2 is None):
        order_c2 = list(np.unique(df[c2]))
    if c3 and (order_c3 is None):
        order_c3 = list(np.unique(df[c3]))
    data = []
    l1 = []
    if c2:
        l2 = []
    else:
        l2 = None
    if c3:
        l3 = []
    else:
        l3 = None
    if not(errorbar_col is None):
        assert errorbar_col in df
        err = []
    else:
        err = None
    for e1 in order_c1:
        data12, lab12 = [], []
        if not(errorbar_col is None):
            err12 = []
        if c2:
            lab2 = []
            for e2 in order_c2:
                if c3:
                    data123, lab123 = [], []
                    if not(errorbar_col is None):
                        err123 = []
                    for e3 in order_c3:
                        res_df = query_df(df, {c1: e1, c2: e2, c3: e3})
                        assert len(res_df) <= 1, res_df
                        if len(res_df) > 0:
                            data123.append(res_df[data_col].iloc[0])
                            lab123.append(e3)
                            if not(errorbar_col is None):
                                err123.append(res_df[errorbar_col].iloc[0])
                    if data123:
                        data12.append(data123)
                        lab12.append(lab123)
                        lab2.append(e2)
                        if not(errorbar_col is None):
                            err12.append(err123)
                else:
                    res_df = query_df(df, {c1: e1, c2: e2})
                    assert len(res_df) <= 1, res_df
                    if len(res_df) > 0:
                        data12.append([res_df[data_col].iloc[0]])
                        if not(errorbar_col is None):
                            err12.append([res_df[errorbar_col].iloc[0]])
                        lab2.append(e2)
            if data12:                
                data.append(data12)
                if c3:
                    l3.append(lab12)
                if not(errorbar_col is None):
                    err.append(err12)
                l2.append(lab2)
                l1.append(e1)
        else:
            res_df = query_df(df, {c1: e1})
            assert len(res_df) <= 1, res_df
            if len(res_df) > 0:
                data.append([[res_df[data_col].iloc[0]]])
                if not(errorbar_col is None):
                    err.append([[res_df[errorbar_col].iloc[0]]])
                l1.append(e1)
    assert data, data
    if labn1 and l1:
        l1 = [labn1[e] for e in l1]
    if labn2 and l2:
        l2 = [[labn2[f] for f in e] for e in l2]
    if labn3 and l3:
        l3 = [[[labn3[g] for g in f] for f in e] for e in l3]
    #FIXME ad hoc
    cols = ['w', (.8, .8, .8, 1), (.4, .4, .4, 1)]#[(1, 1, .8, 1),
    # (1, .9, .9, 1),
    # (.85, .95, 1, 1)]   
    face_colors = [[[cols[i] for g in f]
                        for f in e]
                            for i, e in enumerate(data)]
    edge_colors = [[['y']*len(data[0][0])], [['b']*len(data[0][0])]*2+[['r']*len(data[0][0])]*2, [['b']*len(data[0][0])]*2+[['r']*len(data[0][0])]*2]
         
    level3_bar_aux(data, error_bars=err, face_colors=face_colors, edge_colors=edge_colors,
                   title=None, figsize=None,
                   l1_labels=l3, l2_labels=l2, l3_labels=l1,
                   l3_addlines=l3_addlines, **kwargs)

# rename l1_labels, l2_, l3_ appropriately...
# use **args to pass arguments to aux concisely
# Give possibility to add lines at any level and probably by drawing a line
# rather than using underscores (just need to get text position in axis units)
# Have a function that can work for n levels for arbitrary n.
# get inspiration from seaborn bar plot for interface.

# legend (score types)
# plt.legend(fontsize=26, loc='upper left')

   
    
    
"""
f, ax = plt.subplots(1)
model_abs = [0, 2, 3, 4, 5, 7, 8, 9, 10]
colors = ['y', 'r', 'r', 'r', 'r', 'b', 'b', 'b', 'b']
avg = [(5.156055+6.584990)/2.,
       (4.127968+4.559587)/2.,
       (4.959761+4.344007)/2.,
       (5.281402+4.831002)/2.,
       (5.292484+5.356358)/2.,
       (3.141369+3.644692)/2.,
       (3.942066+5.093100)/2.,
       (8.948050+8.459504)/2.,
       (8.761200+6.820815)/2.,
]
err = [np.sqrt((0.151573**2+0.264920**2)/2.),
       np.sqrt((0.153117**2+0.178218**2)/2.),      
       np.sqrt((0.163609**2+0.175624**2)/2.),
       np.sqrt((0.165038**2+0.196414**2)/2.),
       np.sqrt((0.150689**2+0.209206**2)/2.),
       np.sqrt((0.148835**2+0.215871**2)/2.),
       np.sqrt((0.185682**2+0.270305**2)/2.),
       np.sqrt((0.222184**2+0.383257**2)/2.),
       np.sqrt((0.236593**2+0.276043**2)/2.),
]
bar_list = ax.bar(model_abs, avg, linewidth=5, yerr=err,
                  error_kw={'ecolor': 'k', 'capsize': 10})
for bar, c in zip(bar_list, colors):
    bar.set_facecolor('w')
    bar.set_edgecolor(c)

#ax.set_xticks(np.arange(len(models))+.4)
#texts = ax.set_xticklabels(model_names, fontsize=40)
"""
"""
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
"""



"""
def plot_means(tasks, task_names, models, model_names, matched_lang, m, s, title=u"", filename=None):

        
        
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
"""