#! /usr/bin/env python
from __future__ import division

import argparse
import cPickle as pickle
import imp
import os
from   os.path import join

import numpy as np

from pycog             import RNN
from pycog.figtools    import Figure
from pycog.utils       import get_here, get_parent
from examples.analysis import multisensory

import paper

#=========================================================================================
# Image format
#=========================================================================================

p = argparse.ArgumentParser()
p.add_argument('-f', '--format', default='pdf')
a = p.parse_args()

format = a.format

#=========================================================================================
# Paths
#=========================================================================================

here     = get_here(__file__)
base     = get_parent(here)
figspath = join(here, 'figs')

savefile   = join(base, 'examples', 'work', 'data', 'multisensory', 'multisensory.pkl')
trialsfile = join(paper.scratchpath, 'multisensory', 'trials', 'multisensory_trials.pkl')
sortedfile = join(paper.scratchpath, 'multisensory', 'trials', 'multisensory_sorted.pkl')

# Load model
modelfile = join(base, 'examples', 'models', 'multisensory.py')
m = imp.load_source('model', modelfile)

# Units to display
units = {
    'choice':   87,
    'modality': 123,
    'mixed':    121
    }

#=========================================================================================
# Figure setup
#=========================================================================================

fig = Figure(w=6.3, h=3.9, axislabelsize=7, labelpadx=5, labelpady=5.5, thickness=0.6,
             ticksize=3, ticklabelsize=6, ticklabelpad=2, format=paper.format)

#-----------------------------------------------------------------------------------------
# Inputs
#-----------------------------------------------------------------------------------------

w  = 0.15
dx = w + 0.04
x0 = 0.09
x1 = x0 + dx
x2 = x1 + dx

h  = 0.15
dy = h + 0.05
y0 = 0.79
y1 = y0 - dy

plots = {
    'v_v':  fig.add([x0, y0, w, h]),
    'v_a':  fig.add([x0, y1, w, h]),
    'a_v':  fig.add([x1, y0, w, h]),
    'a_a':  fig.add([x1, y1, w, h]),
    'va_v': fig.add([x2, y0, w, h]),
    'va_a': fig.add([x2, y1, w, h])
    }

#-----------------------------------------------------------------------------------------
# Psychometric function, units
#-----------------------------------------------------------------------------------------

w  = 0.25
dx = w + 0.06
x1 = x0 + dx
x2 = x1 + dx

h  = 0.32
dy = h + 0.18
y0 = y1
y1 = y0 - dy

plots.update({
    'psy':      fig.add([x2, y0, w, h]),
    'choice':   fig.add([x0, y1, w, h]),
    'modality': fig.add([x1, y1, w, h]),
    'mixed':    fig.add([x2, y1, w, h])
    })

#-----------------------------------------------------------------------------------------
# Plot labels
#-----------------------------------------------------------------------------------------

x0 = 0.01
x1 = 0.64
y0 = 0.95
y1 = 0.45

plotlabels = {
    'A': (x0, y0),
    'B': (x1, y0),
    'C': (x0, y1)
    }
fig.plotlabels(plotlabels, fontsize=paper.plotlabelsize)

#=========================================================================================
# Labels
#=========================================================================================

plot = plots['v_v']
plot.ylabel('Visual (a.u.)', fontsize=6)

plot = plots['v_a']
plot.xlabel('Time from stim. onset (ms)')
plot.ylabel('Auditory (a.u.)', fontsize=6)

plot = plots['choice']
plot.xlabel('Time from stim. onset (ms)')
plot.ylabel('Firing rate (a.u.)')

plot = plots['v_v']
plot.text_upper_center('Visual only', dy=0.1, fontsize=7)

plot = plots['a_v']
plot.text_upper_center('Auditory only', dy=0.1, fontsize=7)

plot = plots['va_v']
plot.text_upper_center('Multisensory', dy=0.1, fontsize=7)

plot = plots['choice']
plot.text_upper_center('Choice selectivity', dy=0.1, fontsize=7)

plot = plots['modality']
plot.text_upper_center('Modality selectivity', dy=0.1, fontsize=7)

plot = plots['mixed']
plot.text_upper_center('Mixed selectivity', dy=0.1, fontsize=7)

#=========================================================================================
# Sample inputs
#=========================================================================================

freq0      = int(np.ceil(m.boundary))
boundary_v = m.baseline_in + m.scale_v_p(m.boundary)
boundary_a = m.baseline_in + m.scale_a_p(m.boundary)

rng = np.random.RandomState(1215)
rnn = RNN(savefile, {'dt': 0.5}, verbose=False)
trials = []
for i in xrange(3):
    trial_func = m.generate_trial
    trial_args = {
        'name':     'test',
        'catch':    False,
        'modality': ['v', 'a', 'va'][i],
        'freq':     freq0,
        }
    info = rnn.run(inputs=(trial_func, trial_args), rng=rng)

    dt    = rnn.t[1] - rnn.t[0]
    step  = int(5/dt)
    trial = {
        't':    rnn.t[::step],
        'u':    rnn.u[:,::step],
        'r':    rnn.r[:,::step],
        'z':    rnn.z[:,::step],
        'info': info
        }
    trials.append(trial)

# Display time
epochs = trials[0]['info']['epochs']
stimulus_start, stimulus_end = epochs['stimulus']
t0   = stimulus_start
tmin = 200
tmax = stimulus_end

# Time
t = trials[0]['t']
w = np.where((tmin <= t) & (t <= tmax))
t = t[w] - stimulus_start

prop = dict(lw=0.5, zorder=10)

def plot_inputs(trial, mod, all):
    # Visual input
    r = trial['u'][m.VISUAL_P][w]
    plots[mod+'_v'].plot(t, r, color=multisensory.colors['v'], lw=0.8, zorder=5)
    all.append(r)

    # Auditory input
    r = trial['u'][m.AUDITORY_P][w]
    plots[mod+'_a'].plot(t, r, color=multisensory.colors['a'], lw=0.8, zorder=5)
    all.append(r)

    # Boundaries
    if 'v' in mod:
        plots[mod+'_v'].plot(t, boundary_v*np.ones_like(t),
                             color=Figure.colors('darkblue'), lw=0.75, zorder=10)
    if 'a' in mod:
        plots[mod+'_a'].plot(t, boundary_a*np.ones_like(t),
                             color=Figure.colors('darkgreen'), lw=0.75, zorder=10)

    T  = trial['t']
    W, = np.where((500 < T) & (T <= 1500))
    print(np.std(trial['u'][m.VISUAL_P][W]))
    print(np.std(trial['u'][m.AUDITORY_P][W]))

v, a, va = 3*[False]
all = []
for trial in trials:
    info     = trial['info']
    modality = info['modality']
    freq     = info['freq']

    if freq != freq0:
        continue

    if modality == 'v':
        plot_inputs(trial, 'v', all)
        v = True
    elif modality == 'a':
        plot_inputs(trial, 'a', all)
        a = True
    elif modality == 'va':
        plot_inputs(trial, 'va', all)
        va = True

    if v and a and va:
        break

# Shared axes
names = ['v_v', 'v_a', 'a_v', 'a_a', 'va_v', 'va_a']
fig.shared_lim([plots[p] for p in names], 'y', [0, 1.75], margin=0)
for name in names:
    plot = plots[name]
    plot.xlim(tmin-t0, tmax-t0)
    plot.xticks([tmin-t0, 0, tmax-t0])
    plot.yticks([0, 1])
    if not name.startswith('v_'):
        plot.yticklabels()
    if name != 'v_a':
        plot.xticklabels()

#=========================================================================================
# Psychometric functions
#=========================================================================================

plot = plots['psy']

multisensory.psychometric_function(trialsfile, plot, ms=4.5)

plot.xlabel('Rate (events/sec)')
plot.ylabel('Percent high')

plot.vline(m.boundary, lw=0.5)

prop = {'prop': {'size': 5.5}, 'handlelength': 1,
        'handletextpad': 0.8, 'labelspacing': 0.6}
plot.legend(bbox_to_anchor=(0.455, 1.03), **prop)

plot.text_upper_center('boundary', dy=0.06, fontsize=6)

#=========================================================================================
# Single units
#=========================================================================================

# Load trials
with open(trialsfile) as f:
    trials = pickle.load(f)

all = []
for name, unit in units.items():
    all.append(multisensory.plot_unit(unit, sortedfile, plots[name],
                                      t0=t0, tmin=tmin, tmax=tmax, lw=1.25))
    if name == 'choice':
        pass
        plots[name].ylim(0, 1)
        plots[name].yticks([0, 1])
    elif name == 'modality':
        pass
        plots[name].ylim(0, 0.75)
        plots[name].yticks([0, 0.5])
    elif name == 'mixed':
        pass
        plots[name].ylim(0, 2.5)
        plots[name].yticks([0, 1, 2])

# Legend
prop = {'prop': {'size': 5.5},
        'handlelength': 1.7, 'handletextpad': 1.2, 'labelspacing': 0.5}
plots['choice'].legend(bbox_to_anchor=(0.45, 1.03), **prop)

#=========================================================================================

fig.save(path=figspath)
