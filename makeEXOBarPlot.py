#!/usr/bin/env python
import os, argparse, types, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.transforms as transforms
from EXOAnalysisBar import *   

import csv

#os.system('osascript numbers2csv.scpt')

path = os.getcwd()+'/'

ABs = EXOAnalysisBars()


#----------------------------#------------------------#----------------------#
#
# some global options
#
preliminaryLabel = "Preliminary"                          # "preliminary" label
#preliminaryLabel = ""                          
filename = 'barplot'                           # prefix for output files
#
# command line options
#
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--cadi', '-c', help='always use CADI instead of arXiv number', dest='cadi', \
                        action='store_true', default=False)
parser.add_argument('--verbose', '-v', help='verbose output', dest='verbose', \
                        action='store_true', default=False)
parser.add_argument('--grid', '-g', help='show grid', dest='grid', \
                        action='store_true', default=False)
parser.add_argument('--log', '-l', help='log x scale', dest='logx', \
                        action='store_true', default=False)
parser.add_argument('--batch', '-b', help='batch mode (produce pdf and exit)', dest='batch', \
                        action='store_true', default=False)
parser.add_argument('--input', '-i', help='input csv file', dest='input', type=str, default="B2GBarchartInputTable - ALL.csv")
parser.add_argument('--output', '-o', help='output file', dest='output', type=str, default=None)
parser.add_argument('categories', nargs='+', choices=ABs.categories.keys())
args = parser.parse_args()
verbose = args.verbose
#
# define category
#
if args.categories[0] == 'ALL':
    args.categories = ['DIB', 'RES', 'VHF']#, 'HGB', 'LQ', 'EF', 'CI', 'ED', 'DM', 'OTH']
print (args.categories)
ncat = len(args.categories)



with open(args.input) as csvfile:
    reader = csv.reader(csvfile)
    for ir,row in enumerate(reader):
        if not ir:
            labels = row
        else:
            if row and not row[0]=="":
                auxstring = "ABs.add("+",".join(labels[i]+"=None" if row[i]=="" else labels[i]+'=r"'+row[i]+'"' for i in range(len(row)))+")"
                print(auxstring)
                exec(auxstring)

#------------ body ------------------------#

xmin = 0.
xmax = 1.

AB_categories = {}
nbars_tot = 0
for cat in args.categories:
    AB_categories[cat] = EXOAnalysisCategory(cat,ABs)
    if AB_categories[cat].xmax > xmax: xmax = AB_categories[cat].xmax
    nbars_tot += AB_categories[cat].nbars

print (AB_categories)
print (xmax)
        
if args.logx:
    xmin = 0.20
    xmax = xmax*1.2
else:
    xmin = 0.
    xmax = 1.05*xmax   
    

#
# define canvas size and margins
#
cnvSizeX = 21.*scale
cnvMarginLeft = 7.*scale
cnvMarginRight = 0.3*scale
cnvMarginTop = 1.3*scale
cnvMarginBottom = 1.3*scale
cnvSizeY = (nbars_tot+2)*bar_height+cnvMarginTop+cnvMarginBottom
#
# setup matplotlib
#
#plt.rc('text', usetex=True)
#plt.rc('font', family='sans-serif',sans-serif='Tahoma',style='normal',variant='normal',weight='normal',stretch='condensed')
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
#rcParams['font.sans-serif'] = ['Tahoma']
rcParams['font.sans-serif'] = ['DejaVu Sans']
rcParams['font.stretch'] = 'condensed'


fig = plt.figure(figsize=(cnvSizeX,cnvSizeY))
# adjust plot size
fig.subplots_adjust(left=cnvMarginLeft/cnvSizeX, right=1.-cnvMarginRight/cnvSizeX, \
                    top=1.-cnvMarginTop/cnvSizeY, bottom=cnvMarginBottom/cnvSizeY)
print ([ycat.nbars for ycat in AB_categories.values()])
gs = gridspec.GridSpec(ncat, 1, hspace = 0.0, height_ratios = [ycat.nbars+1 for ycat in AB_categories.values()])

all_axes = []
for icat,AB_category in enumerate(AB_categories.values()):
    ax = AB_category.add_plot(fig,gs[icat],args.cadi,[xmin,xmax],args.logx)
    all_axes.append(ax)
    
all_axes[-1].tick_params(axis='x', which='both', reset=True, top=False, direction='in')
for tl in all_axes[-1].get_xticklabels():
    tl.set_size(0.55*textsize)

if args.grid:
    for ax in all_axes:
        ax.xaxis.grid(True, linestyle='--', color='grey', alpha=0.25)

#------------CMS Headers ------------------------#
thdr3 = "Overview of CMS B2G results"
ax1 = all_axes[0]
ymax = ax1.get_ylim()[1]
gap = ax1.transData.inverted().transform_point(ax1.transAxes.transform_point((0.01,0)))
hdr1 = ax1.text(gap[0],ymax+0.1, \
                r"CMS "+preliminaryLabel+"", \
                horizontalalignment='left',verticalalignment='bottom',color='black',weight='bold',
                size=textsize*0.6)
hdr2 = ax1.text(xmax,ymax+0.1, \
                r"35.9 - 77.3 $\mathrm{fb}^{-1}$ (13 TeV)", \
                horizontalalignment='right',verticalalignment='bottom',color='black',
                size=textsize*0.6)
hdr3 = ax1.text(0.5,0.98, \
                r""+thdr3+"", \
                horizontalalignment='center',verticalalignment='top',color=title_color,weight='bold',
                transform = fig.transFigure,
                size=textsize)
hdr4 = ax1.text(0.97,0.03, \
                r"EPS-HEP 2019", \
                horizontalalignment='right',verticalalignment='bottom',color='black',weight='bold',
                transform = fig.transFigure,
                size=textsize*0.5)

#-------------Foot note--------------------------#
caption = ax1.text(0.03,0.03, \
#                "Selection of observed upper limits at 95% C.L. (theory uncertainties are not included) \nobtained at 13 TeV center of mass energy.",
                "Selection of observed exclusion limits at 95% CL (theory uncertainties are not included).",
                horizontalalignment='left',verticalalignment='center',color='black',
                transform = fig.transFigure,
                size=textsize*0.5)

#--------------Output-----------------------------#

if args.output!=None:
    fname = args.output
else:
    analysis_group = "_".join(args.categories)
    fname = path+filename+"_"+analysis_group
    
plt.savefig(fname=fname+".pdf",format="pdf")
plt.savefig(fname=fname+".svg",format="svg")
plt.savefig(fname=fname+".png",format="png")

if not args.batch:
    plt.show()
sys.exit(0)

#--------------------------------------------------#
