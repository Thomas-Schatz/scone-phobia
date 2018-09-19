# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 12:56:29 2018

@author: Thomas Schatz

Utility functions around seaborn.catplot for easier customization of plots.
"""

import numpy as np
import seaborn as sns
import matplotlib.patches as patches


def catplot_abscissa(x_order, hue_order=None, xtype='center'):
    """
    Returns a dict that contains, for each possibly combination of x and hue
    values, the abscissa of the corresponding bar in any Facet of a
    seaborn 'bar' catplot called with x_order and hue_order as arguments. 
    
    Depending on the value of xtype, the abscissas of the center, left or right
    of the bars is returned.
    """
    assert xtype in ['center',  'left', 'right']
    delta = .5 if xtype=='center' else (0. if xtype=='left' else 1)
    origin = 0
    grp_stride = 1
    grp_width = .8
    if hue_order is None:
        nb_hues = 1
    else:
        nb_hues = len(hue_order)
    bar_width = grp_width/float(nb_hues)
    d = {}
    for i, xval in enumerate(x_order):
        if not(hue_order is None):
            for j, hval in enumerate(hue_order):
                d[xval, hval] =  origin + grp_stride*i - grp_width/2. +\
                                    (j+delta)*bar_width
        else:
            # if no hues, groups contain a single bar
            d[xval] = origin + grp_stride*i - grp_width/2. + delta*grp_width
    return d


def set_order(param, order_param, kwargs, data): 
    # this has a side-effect on kwargs          
    if not(order_param in kwargs):
        kwargs[order_param] = np.unique(data[param])
    return kwargs[order_param]


def custom_catplot(x, y, yerr, data, col=None, row=None, hue=None,
                       err_args=None, **kwargs):
    """
    Seaborn catplot with kind='bar'
    that uses a column of the data frame to determine
    the length of the errorbars.
    
    The dataframe is assumed to contain pre-computed central tendency and
    variability estimates (e.g. means and standard deviations instead of raw
    values).
    """
    if 'kind' in kwargs:
        assert kwargs['kind'] == 'bar', kwargs['kind']
    else:
        kwargs['kind'] = 'bar'    
    x_order = set_order(x, 'order', kwargs, data)
    if hue:
        hue_order = set_order(hue, 'hue_order', kwargs, data)
    else:
        hue_order = None
    if col:
        col_order = set_order(col, 'col_order', kwargs, data)
    else:
        col_order = [None]
    if row:
        row_order = set_order(row, 'row_order', kwargs, data)
    else:
        row_order = [None]
    g = sns.catplot(x=x, y=y, data=data, hue=hue, col=col, row=row, **kwargs)    
    x_dict = catplot_abscissa(x_order, hue_order, xtype='center')
    if hue:
        xs = [x_dict[e, f] for e in x_order for f in hue_order]
    else:
        xs = [x_dict[e] for e in x_order]
    for i, coli in enumerate(col_order):
        if coli is None:
            col_ind = True
        else:
            col_ind = data[col] == coli
        for j, rowj in enumerate(row_order):
            if rowj is None:
                row_ind = True
            else:
                row_ind = data[row] == rowj
            ys, yerrs = [], []
            for e in x_order:
                df_e = data[col_ind & row_ind & (data[x] == e)]
                if hue:
                    ys = ys + [float(df_e[df_e[hue] == f][y])
                                for f in hue_order]
                    yerrs = yerrs + [float(df_e[df_e[hue] == f][yerr])
                                        for f in hue_order]
                else:
                    ys.append(float(df_e[y]))
                    yerrs.append(float(df_e[yerr]))
            if err_args is None:
                err_args = {}
            g.axes[j, i].errorbar(xs, ys, yerrs,
                                  linestyle='None', marker='None', **err_args)
    return g, x_dict


def within_tol(a, b, eps):
    res = True
    for e, f in zip(a, b):
        if not(abs(e-f) < eps):
            res = False
            break
    return res


def set_edgecolor(ax, x_order, hue_order, f, line_width=None):
    """
    Function to customize the colors of the edges in a seaborn catplot.
    Probably won't give a nice result if the edgecolor is not shared by
    bars from a same group (hue).
    
    Will need to be adapted if we want to use it on a graph without hues.
    On graph with several facets, needs to be applied iteratively to each
    facet.
    """
    # get dict indicating abscissa of each bar
    xl = catplot_abscissa(x_order, hue_order, 'left')
    rectangles = [e for e in ax.get_children()
                    if isinstance(e, patches.Rectangle)]             
    # filter out spurious rectangles whose origin I don't understand
    rectangles = [e for e in rectangles if not(e.get_width() == 1 and \
                                               e.get_height() == 1 and \
                                               e.get_xy() == (0, 0))]                                              
    # identify id of remaining rectangles based on abscissa and color
    eps = 10**-8
    for x_cond in x_order:
        for h_cond in hue_order:
            xy = (xl[x_cond, h_cond], 0.)
            bars = [e for e in rectangles if within_tol(e.get_xy(), xy, eps)]
            assert len(bars) == 1, (bars, xy)
            bar = bars[0]
            bar.set_edgecolor(f(x_cond, h_cond))
            if not(line_width is None):
                bar.set_linewidth(line_width)