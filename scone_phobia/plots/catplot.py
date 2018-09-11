# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 12:56:29 2018

@author: Thomas Schatz

Utility functions around seaborn.catplot for easier customization of plots.
"""

import numpy as np
import seaborn as sns


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
