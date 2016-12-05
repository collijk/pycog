#! /usr/bin/env python
from __future__ import division

import cPickle as pickle
import imp
import os
import sys
from   os.path import join

import numpy as np

from pycog             import RNN
from pycog.figtools    import Figure, mpl
from pycog.utils       import get_here, get_parent
from examples.analysis import romo

import paper

#=========================================================================================
# Paths
#=========================================================================================

here     = get_here(__file__)
base     = get_parent(here)
figspath = join(here, 'figs')

modelfile  = join(base, 'examples', 'models', 'romo.py')
savefile   = join(base, 'examples', 'work', 'data', 'romo', 'romo.pkl')
trialsfile = join(paper.scratchpath, 'romo', 'trials', 'romo_trials.pkl')
sortedfile = join(paper.scratchpath, 'romo', 'trials', 'romo_sorted.pkl')

#=========================================================================================
# Setup
#=========================================================================================

# Load model
m = imp.load_source('model', modelfile)

units = {
    'L': 18,
    'R': 125,
    }

# Color map
cmap = mpl.cm.jet
norm = mpl.colors.Normalize(vmin=m.fmin, vmax=m.fmax)
smap = mpl.cm.ScalarMappable(norm, cmap)

#=========================================================================================
# Figure setup
#=========================================================================================

w   = 6.3
h   = 4
r   = w/h
fig = Figure(w=w, h=h, axislabelsize=7, labelpadx=5, labelpady=5.5,
             thickness=0.6, ticksize=3, ticklabelsize=6, ticklabelpad=2,
             format=paper.format)

#-----------------------------------------------------------------------------------------
# Inputs
#-----------------------------------------------------------------------------------------

w  = 0.25
dx = w + 0.04
x0 = 0.09

h  = 0.165
dy = h + 0.045
y0 = 0.78
y1 = y0 - dy

plots = {
    '>': fig.add([x0, y0, w, h]),
    '<': fig.add([x0, y1, w, h])
    }

#-----------------------------------------------------------------------------------------
# Psychometric function, units
#-----------------------------------------------------------------------------------------

dx = w + 0.06
x1 = x0 + dx
x2 = x1 + dx

w_psy = 0.27
h_psy = 0.32
x_psy = x1 - 0.02
y_psy = y1

h  = 0.32
dy = h + 0.16
y0 = y1
y1 = y0 - dy

x_tune = x2
y_tune = y0
w_tune = w
h_tune = 0.15

w_a1    = 0.07
h_a1    = r*w_a1
x_stim  = x_tune + 0.025
x_delay = x_stim + w_a1 + 0.08
y_a1    = y0 + h_tune + 0.11

x_sig = x2 + 0.015
w_sig = 0.235

plots.update({
    'psy':   fig.add([x_psy, y_psy, w_psy, h_psy]),
    'L':     fig.add([x0, y1, w, h]),
    'R':     fig.add([x1, y1, w, h]),
    'sig':   fig.add([x_sig, y1, w_sig, h]),
    'tune':  fig.add([x_tune, y_tune, w_tune, h_tune]),
    'stim':  fig.add([x_stim, y_a1,   w_a1,   h_a1]),
    'delay': fig.add([x_delay, y_a1,   w_a1,   h_a1])
    })

#-----------------------------------------------------------------------------------------
# Plot labels
#-----------------------------------------------------------------------------------------

x0 = 0.01
x1 = 0.37
x2 = 0.63
x3 = 0.66
y0 = 0.93
y1 = 0.445

plotlabels = {
    'A': (x0, y0),
    'B': (x1, y0),
    'C': (x2, y0),
    'D': (x0, y1),
    'E': (x3, y1)
    }
fig.plotlabels(plotlabels, fontsize=paper.plotlabelsize)

#=========================================================================================
# Labels
#=========================================================================================

plot = plots['tune']
plot.xlabel('Time from $f_1$ onset (sec)')
plot.ylabel('Pearson $r$', labelpad=2)

plot = plots['stim']
plot.xlabel('$a_1$ (stim)', labelpad=3)
plot.ylabel('$a_1$ (end delay)', labelpad=2)

plot = plots['delay']
plot.xlabel('$a_1$ (mid-delay)', labelpad=3)
plot.ylabel('$a_1$ (end delay)', labelpad=2)

plot = plots['L']
plot.xlabel('Time from $f_1$ onset (sec)')
plot.ylabel('Firing rate (a.u.)')

plot = plots['L']
plot.text_upper_center('Positively tuned', dy=0.1, fontsize=7)

plot = plots['R']
plot.text_upper_center('Pos. tuned during $f_1$, neg. during $f_2$', dy=0.1, fontsize=7)

plot = plots['<']
plot.xlabel('Time from $f_1$ onset (sec)')
plot.ylabel('Input (a.u.)')

plot = plots['sig']
plot.ylabel('Prop. sig. tuned units')

#=========================================================================================
# Sample inputs
#=========================================================================================

rng = np.random.RandomState(1066)
rnn = RNN(savefile, {'dt': 2}, verbose=False)

trial_func = m.generate_trial
trial_args = {
    'name':  'test',
    'catch': False,
    'fpair': (34, 26),
    'gt_lt': '>'
    }
info = rnn.run(inputs=(trial_func, trial_args), rng=rng)

# Stimulus durations
epochs = info['epochs']
f1_start, f1_end = epochs['f1']
f2_start, f2_end = epochs['f2']
t0   = f1_start
tmin = 0
tmax = f2_end

t     = 1e-3*(rnn.t-t0)
delay = [1e-3*(f1_end-t0), 1e-3*(f2_start-t0)]
yall  = []

# f1 > f2
plot = plots['>']
plot.plot(t, rnn.u[0], color=Figure.colors('orange'), lw=0.5)
yall.append(rnn.u[0])
plot.xticklabels()

trial_args = {
    'name':  'test',
    'catch': False,
    'fpair': (34, 26),
    'gt_lt': '<'
    }
info = rnn.run(inputs=(trial_func, trial_args), rng=rng)

# f1 < f2
plot = plots['<']
plot.plot(t, rnn.u[0], color=Figure.colors('purple'), lw=0.5)
yall.append(rnn.u[0])

# Shared axes
input_plots = [plots['>'], plots['<']]
ymin, ymax = fig.shared_lim(input_plots, 'y', yall, lower=0)
for plot in input_plots:
    plot.xlim(t[0], t[-1])
    plot.xticks([0, 1, 2, 3, 4])
    plot.yticks([0, 1])

# Delay epoch
plot = plots['>']
plot.plot(delay, 1.1*ymax*np.ones(2), color='k', lw=1.5)
plot.text(np.mean(delay), 1.15*ymax, 'Delay', ha='center', va='bottom', fontsize=5.5)

# Conditions
plots['>'].text(np.mean(delay), 0.9*ymax, '$f_1 > f_2$', ha='center', va='top',
                color=Figure.colors('orange'), fontsize=6)
plots['<'].text(np.mean(delay), 0.9*ymax, '$f_1 < f_2$', ha='center', va='top',
                color=Figure.colors('purple'), fontsize=6)

#=========================================================================================
# Psychometric functions
#=========================================================================================

plot = plots['psy']

romo.psychometric_function(trialsfile, plot, smap=smap, fontsize=6.5, lw=1)
plot.xlabel('$f_1$ (Hz)')
plot.ylabel('$f_2$ (Hz)')

#=========================================================================================
# Tuning analysis
#=========================================================================================

romo.tuning_corr(trialsfile, sortedfile,
                 plot_corr=plots['tune'],
                 plot_sig=plots['sig'],
                 plot_stim=plots['stim'],
                 plot_delay=plots['delay'],
                 t0=t0, ms=1.5)

plot = plots['tune']
plot.ylim(-0.5, 1)
plot.highlight(1e-3*(f1_start-t0), 1e-3*(f1_end-t0))
plot.highlight(1e-3*(f1_start-t0), 1e-3*(f1_end-t0))
plot.xticks([0, 1, 2, 3])
plot.yticks([0, 1])

plot = plots['sig']
plot.highlight(1e-3*(f1_start-t0), 1e-3*(f1_end-t0))
plot.highlight(1e-3*(f1_start-t0), 1e-3*(f1_end-t0))
plot.highlight(1e-3*(f2_start-t0), 1e-3*(f2_end-t0))
plot.highlight(1e-3*(f2_start-t0), 1e-3*(f2_end-t0))
plot.xticks([0, 1, 2, 3, 4])
plot.yticks([0, 0.5, 1])

plot = plots['stim']
plot.xlim(-0.3, 0.3); plot.xticks([-0.3, 0, 0.3])
plot.ylim(-0.3, 0.3); plot.yticks([-0.3, 0, 0.3])

plot = plots['delay']
plot.xlim(-0.4, 0.4); plot.xticks([-0.4, 0, 0.4])
plot.ylim(-0.4, 0.4); plot.yticks([-0.4, 0, 0.4])

#=========================================================================================
# Single units
#=========================================================================================

yall = []
for name, unit in units.items():
    plot = plots[name]
    yall.append(romo.plot_unit(unit, sortedfile, plot, smap,
                               t0=t0, tmin=tmin, tmax=tmax, lw=1.25))
    plot.xticks([0, 1, 2, 3, 4])

    if name == 'L':
        plot.ylim(0, 0.75)
        plot.yticks([0, 0.5])

        ymin, ymax = plot.get_ylim()
        plot.text(1e-3*((f1_start + f1_end)/2 - t0), 1.03*ymax, '$f_1$',
                  ha='center', va='bottom', fontsize=7)
        plot.text(1e-3*((f2_start + f2_end)/2 - t0), 1.03*ymax, '$f_2$',
                  ha='center', va='bottom', fontsize=7)
    elif name == 'R':
        plot.ylim(0, 0.75)
        plot.yticks([0, 0.5])

    # Highlight stimulus periods
    plot.highlight(1e-3*(f1_start-t0), 1e-3*(f1_end-t0))
    plot.highlight(1e-3*(f2_start-t0), 1e-3*(f2_end-t0))

#=========================================================================================

fig.save(path=figspath)
