#!/usr/bin/env python3
from pickle import dump, load
from datetime import datetime
import os.path
import argparse
import osense
import pandas as pd
#import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    'firstcycle',
    help='first cycle to process, format YYYY-MM-DD-HH',
    type=lambda s: datetime.strptime(s, '%Y-%m-%d-%H'))
parser.add_argument(
    'lastcycle',
    help='last cycle to process, format YYYY-MM-DD-HH',
    type=lambda s: datetime.strptime(s, '%Y-%m-%d-%H'))
parser.add_argument('indir', help='directory to read in reduced osense files')
parser.add_argument('outdir', help='directory to save stat files')
args = parser.parse_args()

firstcycle = args.firstcycle
lastcycle = args.lastcycle
indir = args.indir
outdir = args.outdir

grouping = 'chan'
norms = ['osense_kin', 'osense_dry', 'osense_moist']
moments = ['mean impact', 'total impact', 'obs count']

cycles = osense.make_cycles(firstcycle, lastcycle)

allthemoments = {}

print('running from', firstcycle, 'to', lastcycle)

# read in all osense data for each cycle and do per-cycle stats
for cycle in cycles:

    CDATE = cycle.strftime("%Y%m%d%H")

    infilename = os.path.join(indir, 'osense_' + CDATE + '.pkl')

    if not os.path.isfile(infilename):
        print(infilename + ' doesn\'t exist, skipping')
        continue

    print('loading  ' + infilename)
    with open(infilename, 'rb') as infile:
        [exp, cdate, osensedata] = load(infile)

    osensedata=osensedata.loc[osensedata.assimilated==1]

    columns = [grouping] + norms

# get the obs with satellite data
    sats = osensedata['source'].loc[osensedata['indxsat'] > 0]
    sources = sats.unique()

    for source in sources:

        osensebysource = osensedata[columns].loc[osensedata['source'] == source]

        meanimpacts = osensebysource.groupby(grouping).mean()
        sumimpacts = osensebysource.groupby(grouping).sum()
        obcounts = osensebysource.groupby(grouping).count()
        # the channels keep getting converted to floats, so fix it here
        meanimpacts.index=meanimpacts.index.astype('int64')
        sumimpacts.index=sumimpacts.index.astype('int64')
        obcounts.index=obcounts.index.astype('int64')

        mymoments = {}

        for norm in norms:
            myframe = {'mean impact': meanimpacts[norm],
                       'total impact': sumimpacts[norm],
                       'obs count': obcounts[norm]}

            mymoments[norm] = myframe

        allthemoments[source] = mymoments

# save for later use
    outfilename = os.path.join(outdir, 'osensestatschans_' + CDATE + '.pkl')
    print("saving file ", outfilename)
    with open(outfilename, 'wb') as outfile:
        dump([{'exp': exp, 'cdate': cdate, 'data': allthemoments}], outfile)


# create a 3-level dictionary for each instrument, norm, and moment
comprehensive = {}

for source in sources:
    sourcedict = {}
    for norm in norms:
        normdict = {}
        for moment in moments:
            normdict[moment] = pd.DataFrame()
        sourcedict[norm] = normdict
    comprehensive[source] = sourcedict

# collect all per-cycle stats for each norm and each instrument
for cycle in cycles:

    CDATE = cycle.strftime("%Y%m%d%H")

    infilename = os.path.join(outdir, 'osensestatschans_' + CDATE + '.pkl')

    if not os.path.isfile(infilename):
        print(infilename + ' doesn\'t exist, skipping')
        continue

    print('loading  ' + infilename)
    with open(infilename, 'rb') as infile:
        [bundle] = load(infile)

    data = bundle['data']

    for source in data.keys():
        for norm in data[source].keys():
            for moment in data[source][norm].keys():
                dataframe = comprehensive[source][norm][moment]
                mycolumn = data[source][norm][moment]
                mycolumn.name = cycle # for unique identification
                dataframe = pd.concat([dataframe, mycolumn], axis=1)
                comprehensive[source][norm][moment] = dataframe


# now caculate the aggregated stats
aggregated = {}

for source in sources:
    sourcedict = {}
    for norm in norms:
        normdict = {}
        normdict['mean total impact'] = \
            comprehensive[source][norm]['total impact'].mean(axis=1)
        normdict['mean num obs'] = \
            comprehensive[source][norm]['obs count'].mean(axis=1)
        normdict['mean impact per ob'] = normdict['mean total impact'] / \
            normdict['mean num obs']
        sourcedict[norm] = normdict
    aggregated[source] = sourcedict
    
outfilename = os.path.join(outdir, 'osensestats_channels_all.pkl')
print("saving file ", outfilename)
with open(outfilename, 'wb') as outfile:
    dump([{'exp': exp, 'firstcycle':firstcycle, 'lastcycle':lastcycle, 'stats': aggregated}], outfile)





