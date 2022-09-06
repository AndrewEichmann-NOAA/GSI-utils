#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 14:23:41 2022

@author: mossland
"""
# Default imports
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import pickle
import datetime
import os.path
import matplotlib.colors as colors
import matplotlib.cm as cmx

#CDATE = '2022011000'
#CDATE = '2021123000'
#CDATE = '2020122600'
#CDATE = '2021011000'
CDATE = '2021010600'


exp='rodeo'
#exp='baily'

#datadir='/work2/noaa/stmp/aeichman/comrot/' + exp + '/osense/'
#datadir='/work/noaa/stmp/aeichman/comrot/' + exp + '/osense/'
rootdir = '/Users/mossland/Desktop/work/EFSOI/' + exp 
indir = rootdir + '/consolidated/'

outdir='/Users/mossland/Desktop/work/EFSOI/rodeo/geoplots/'

filename = indir + 'osense_' + CDATE + '.pkl'
infile = open( filename ,'rb')
[ exp,idata, osensedata ] = pickle.load(infile)
infile.close()


# drop message='NA'/message02='Empty'
# data not dumped/not used
#indices=osensedata[osensedata['assimilated']==0].index
#osensedata.drop(indices,inplace = True)

osensedata=osensedata[osensedata['assimilated']==1]

source = 'Radiosonde'
source = 'AMSUA'
source = 'Ocean_Surface'
source = 'Aircraft'

sources = osensedata.source.unique()

#for source in sources:
#for source in ['Radiosonde','AMSUA','Ocean_Surface','Aircraft']:
for source in sources:

    sourcestr = str( source )
    print('doing ' + sourcestr )

    lon = osensedata.loc[osensedata['source'] == source ]['lon']
    
    lon = osensedata.loc[osensedata['source'] == source ]['lon']
    lat = osensedata.loc[osensedata['source'] == source ]['lat']
    vals = osensedata.loc[osensedata['source'] == source ]['osense_moist']
 
    stuff = osensedata.loc[osensedata['source'] == source
                           ][['osense_moist','lat','lon']]
    stuff['lon']=round(stuff['lon'])
    stuff['lat']=round(stuff['lat'])
    
    foo=stuff.groupby(['lat','lon'],as_index=False).mean()
    count=stuff.groupby(['lat','lon'],as_index=False).count()    
    bar=foo.abs().sort_values(by='osense_moist')
#    bar=foo.sort_values(by='osense_moist')
    baz=foo.iloc[bar.index]
    bazcnt=count.iloc[bar.index]

    vals = baz.osense_moist



    valmean = vals.mean()
    valsstd = foo.osense_moist.std()
    vmin = -valsstd
    vmax = valsstd 

    
    print('vmin, vmax: ' , vmin,vmax)
    rnbw = cm = plt.get_cmap('rainbow')
    rnbw = cm = plt.get_cmap('RdBu')
    rnbw = cm = plt.get_cmap('coolwarm')
    cNorm  = colors.Normalize(vmin=vmin, vmax=vmax)
    
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=rnbw)
    scalarMap.set_array(vals)
    
    colorVal = scalarMap.to_rgba(vals)
    
    title = sourcestr + ' ' + CDATE +', assimilated'
    
    
    fig = plt.figure(figsize=(10,6), dpi=300)
    ax = fig.add_subplot(1, 1, 1,
                         projection=ccrs.PlateCarree(),
                         title=title)
#    ax.set_extent([0, 360, -90, 90])
    ax.set_extent([-180, 180, -90, 90 ])
    s=2*bazcnt.osense_moist
#    ax.scatter(lons, lats,c=colorVal, marker='s',s=s)
    ax.scatter(baz.lon, baz.lat,c=colorVal, marker='.',s=s)
    ax.scatter(-60, 60,facecolors='none', edgecolors='yellow',  marker='o',s=20000)  # 2021010600
 #   ax.scatter(-150, 60,facecolors='none', edgecolors='yellow',  marker='o',s=10000)  # 2021011000
#    ax.scatter(-140, 50,facecolors='none', edgecolors='yellow',  marker='o',s=6000)  # 2020122600
#    ax.scatter(-70, 45,facecolors='none', edgecolors='yellow',  marker='o',s=3000)  # 2020122600
    ax.coastlines()
    ax.gridlines()
    filename=outdir + CDATE + '_' + sourcestr + '.png'
    fig.savefig(filename)


