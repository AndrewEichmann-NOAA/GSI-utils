#!/usr/bin/env python3
import matplotlib       # Matplotlib to make graphics
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker 
matplotlib.use('Agg')   # Need this to generate figs when not running an Xserver (e.g. via PBS/LSF)
from pickle import load
from datetime import datetime
import os.path
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('indir', help='directory to read in osense stat files')
parser.add_argument('outdir', help='directory to save plots')
args = parser.parse_args()

indir = args.indir
outdir = args.outdir
ytickthreshold=25
defaulthorzsize=10
defaultvertsize=6
defaulttickspacing=1

infilename = os.path.join(indir, 'osensestats_channels_all.pkl')

print('loading  ' + infilename)
with open(infilename, 'rb') as infile:
    [bundle] = load(infile)

firstcycle=bundle['firstcycle']
lastcycle=bundle['lastcycle']
exp=bundle['exp']

start = firstcycle.strftime("%Y-%m-%d")
end = lastcycle.strftime("%Y-%m-%d")

stats=bundle['stats']

for source in stats.keys():
    moist=stats[source]['osense_moist']

    tick_spacing=defaulttickspacing
    vertsize=defaultvertsize
    horzsize=defaulthorzsize
    numchans=len(moist['mean total impact'])
    
    if numchans > ytickthreshold:
        tick_spacing=round(numchans/ytickthreshold)
        vertsize=vertsize*tick_spacing
        

    print(source + ' ' + str(numchans) + ' ' + str(tick_spacing))        
        
    filename = os.path.join(outdir, exp + '_' + source + '_meantotal.png')
    title = source + ' mean total impact per cycle (J/kg), ' + \
        exp + ' ' + start + ' to ' + end
    ax = moist['mean total impact'].sort_index(ascending=False).plot.barh(
        xlabel='channel',
        ylabel='J/kg',
        title=title,
        figsize=(horzsize, vertsize)
    )
    ax.grid(True)
    fig = ax.get_figure()
    print('saving' + filename)
    fig.savefig(filename, bbox_inches='tight')
    fig.clear()
    
    filename = os.path.join(outdir, exp + '_' + source + '_obspercycle.png')
    title = source+ ' mean observations per cycle, ' + exp + ' ' + start + ' to ' + end
    ax = moist['mean num obs'].sort_index(ascending=False).plot.barh(
        title=title,
        figsize=(horzsize, vertsize),
        xlabel='channel',
        ylabel='J/kg'
    )
    ax.grid(True)
    fig = ax.get_figure()
    print('saving' + filename)
    fig.savefig(filename, bbox_inches='tight')
    fig.clear()
    
    filename = os.path.join(outdir, exp + '_' + source + '_impactperobs.png')
    title = source + ' impact per observation (J/kg), ' + exp + ' ' + start + ' to ' + end
    ax = moist['mean impact per ob'].sort_index(ascending=False).plot.barh(
        xlabel='channel',
        ylabel='J/kg',
        title=title,
        figsize=(horzsize, vertsize)
    )
    ax.grid(True)
    fig = ax.get_figure()
    print('saving' + filename)
    fig.savefig(filename, bbox_inches='tight')
    fig.clear()
