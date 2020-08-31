from math import *
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.transforms as transforms
from matplotlib.ticker import ScalarFormatter
import matplotlib.patches as patches
#----------------------------#Configure plot from here#----------------------#
scale = 0.5
textsize = 30.*scale
bar_color = 'xkcd:light orange'
bar_edge_color = 'xkcd:royal blue'
yaxis_label_color = 'black'
section_text_color = 'xkcd:royal blue'
desc_text_color = 'xkcd:royal blue'
title_color = 'xkcd:dark orange'
bar_height  =  0.30*scale
#
# Class describing input for one bar in the summary plot.
#
class EXOAnalysisBar:

    def __init__(self,category="Other",name=None,pub=None,cadi=None,paper=None,lumi=None,model=None,comment=None,\
                 finalstate=None,parameter=None,lower=None,upper=None,flag=None):
        self.category = category               # model category
        print(self.category)
        self.name = name                       # (unique) name. Reserved names: "line", ""
        self.pub = pub if not pub == None else ""
        self.cadi = cadi
        self.paper = paper
        self.lumi = lumi if not lumi == None else ""
        self.model = model
#        self.comment = comment if not comment == None else ""
        self.comment = comment
        self.finalstate = finalstate
        self.parameter = parameter if not lumi == None else ""
        self.lower = float(lower) if not lower==None else 0.
        self.upper = float(upper) if not upper==None else 0.
        self.flag = float(flag)if not flag==None else 0.
        
        print(self.model,self.comment)
        if self.model == None:
            self.header = ""
        elif self.comment == None:
            self.header = self.model
        else:
            self.header = ", ".join((self.model,self.comment))
        print("==>",self.header)
        
    def __str__(self):
        ''' Show object as string.
        '''
        result = "Analysis "+self.name
        if self.category: result += "\n  Category: "+self.category
        if self.header: result += "\n    Model: "+self.header
        if self.parameter: result += "\n    Parameter: "+self.parameter
        if self.barleft: result += "\n    FS-pub: "+self.barleft
        if self.lower and self.upper: result += "\n    Limits: "+str(self.lower)+","+str(self.upper)
        return result

#
# Container for AnalysisBar objects
#
class EXOAnalysisBars:

    def __init__(self,category=None):
        self.allBars = [ ]
        self.barsPerCat = { }

        self.categories = { 'DIB' : { 'name_tex' : "Dibosons", 'name_size' : 1., 'color' : 'xkcd:baby blue' },
                            'RES' : { 'name_tex' : "Resonances", 'name_size' : 1., 'color' : 'xkcd:blush' },
                            'VHF' : { 'name_tex' : "Very Heavy Fermions", 'name_size' : 1., 'color' : 'xkcd:light olive' },
                            'DM' : { 'name_tex' : "Dark Matter", 'name_size' : 1., 'color' : 'xkcd:baby blue' }, 
                            'HGB' : { 'name_tex' : "Heavy Gauge Bosons", 'name_size' : 1., 'color' : 'xkcd:apricot' },
                            'LQ' : { 'name_tex' : "Leptoquarks", 'name_size' : 1., 'color' : 'xkcd:wheat' },
                            'EF' : { 'name_tex' : "Excited\nFermions", 'name_size' : 1., 'color' : 'xkcd:light olive' },
                            'ED' : { 'name_tex' : "Extra Dimensions", 'name_size' : 1., 'color' : 'xkcd:lavender' },
                            'CI' : { 'name_tex' : "Contact\nInteractions", 'name_size' : 1., 'color' : 'xkcd:blush' },
                            'LL' : { 'name_tex' : "Long-lived", 'name_size' : 1., 'color' : 'cornflowerblue' },
                            'OTH' : { 'name_tex' : "Other", 'name_size' : 1., 'color' : 'silver' },
                            'RPV' : { 'name_tex' : "RPV", 'name_size' : 1., 'color' : 'cornflowerblue' },
                            'ALL' : {} }

    def add(self,category=None,name=None,pub=None,cadi=None,paper=None,lumi=None,model=None,comment=None,\
                 finalstate=None,parameter=None,lower=None,upper=None,flag=None):
        if category==None: category = "Other"
        if flag==None: flag='0'
#        print('name:',name,'flag:',flag)
        if not name or flag=='0':
            print(cadi+": no analysis bar added")
            return
        al = EXOAnalysisBar(category,name,pub,cadi,paper,lumi,model,comment,finalstate,parameter,lower,upper,flag)
        self.allBars.append(al)
        if not category in self.barsPerCat:
            assert category in self.categories
            self.barsPerCat[category] = [ ]
        self.barsPerCat[category].append(al)
        print('flag:',self.barsPerCat[category][-1].flag)
        self.barsPerCat[category].sort(key=lambda x: x.flag)

    def getBars(self,category=None):
        if category==None:
            return self.allBars
        else:
            return self.barsPerCat[category]
        
class EXOAnalysisCategory:
    
    def __init__(self,category,ABs):
        self.ABs_list = ABs.getBars(category)
        
        self.name_tex = ABs.categories[category]["name_tex"]
        self.name_size = ABs.categories[category]["name_size"]
        self.bar_color = ABs.categories[category]["color"]
        
        self.bar_positions = [ ]   # y-position of the bar (= index)
        self.bar_vlows = [ ]       # lower limits
        self.bar_vhighs = [ ]      # upper limits
        self.bar_vdiffs = [ ]      # difference between upper and lower
        self.bar_labels = [ ]      # bar labels
        
        self.xmax = 0.
        self.ax = None
        
        index = 0
        for al in self.ABs_list[::-1]:
            self.bar_positions.append(index+1)
            if al.lower==None:
                self.bar_vlows.append(0.)
            else:
                self.bar_vlows.append(al.lower)
            # set upper limit
            self.bar_vhighs.append(al.upper)
            # set label (in mathmode and bold)
            self.bar_labels.append(r""+al.parameter+"")
            # keep trace of maximum limit
            if al.upper>self.xmax:  self.xmax = al.upper

            index += 1
        self.nbars = index
        #
        # bars are stacked: subtract lower limits
        #
        for i in range(self.nbars):
            self.bar_vdiffs.append(self.bar_vhighs[i]-self.bar_vlows[i])
       
    def add_plot(self,fig,gs,cadi,xlim,logx):
        ax = fig.add_subplot(gs)
        self.ax = ax
        transFD = transforms.blended_transform_factory(fig.transFigure, ax.transData)
        
        # define stacked bars (lower and upper limit)
        barsLow = ax.barh(self.bar_positions,self.bar_vlows,align='center',height=0.75,color='white',tick_label=self.bar_labels)
        barsHigh = ax.barh(self.bar_positions,self.bar_vdiffs,align='center',height=0.85,color=self.bar_color,
                        left=self.bar_vlows,tick_label=self.bar_labels)
        assert len(ax.get_yticklabels())==len(barsHigh)
        # absolute bar height(inch) * relative height * 72 points/inch)
        bar_height_points = bar_height*barsHigh[0].get_height()*72
        
        for i in range(len(barsHigh)):
            ax.get_yticklabels()[i].set_size(0.6*bar_height_points)
            ax.get_yticklabels()[i].set_color(yaxis_label_color)

        ax.set_xlabel(r"mass scale [TeV]",weight='bold',size=0.85*bar_height_points)
        
        # x-axis tick marks inside the plot; no y-axis tick marks
        ax.tick_params(axis='x',which='both',length=0.,labelsize=0.)
        ax.tick_params(axis='y',length=0.)
        # leave 5% space on x-axis
        ax.set_xlim(xlim)
        ax.set_ylim([0,self.nbars+1])
        if logx: plt.xscale('log')
        import numpy as np
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(np.arange(1., 10., 1.))
        ax.xaxis.set_major_formatter(ScalarFormatter())
        
        box = patches.Rectangle((0.01,0.2),0.028,(self.nbars+1)-0.4,
                                fill=True, transform=transFD, clip_on=False, color=self.bar_color)
        ax.add_patch(box)
        
        if not self.name_tex == None:
#            tx = ax.text(0.03, 0.5*(self.nbars+1), r"\textbf{"+self.name_tex+"}",
#                         horizontalalignment='center', verticalalignment='center',
#                         transform=transFD, rotation='vertical', size=self.name_size*0.85*bar_height_points)
            tx = ax.text(0.025, 0.5*(self.nbars+1), self.name_tex, usetex=False,
                         horizontalalignment='center', verticalalignment='center', weight='bold',
                         transform=transFD, rotation='vertical', size=self.name_size*0.6*bar_height_points)
        
        #
        # add text to the bars. Start from bottom.
        #
        index = 0
        bar_texts = [ ]
        
        for al in self.ABs_list[::-1]:
            # use CADI or arXiv numbers
            if cadi:
                Pas_Label = al.cadi
            else:
                Pas_Label = al.pub

            #
            # analysis description and references
            #
            # 1% from right border; centered with bar in y
            gap = ax.transData.inverted().transform_point(ax.transAxes.transform_point((0.002,0)))
            
            xloc = gap[0] + self.bar_vlows[index]
            xloclim = self.bar_vhighs[index]
            if logx:
                xloclim = xloclim / exp(gap[0]*0.1)
            else:
                xloclim -= gap[0]
            
#            print (xloc)
            yloc = barsHigh[index].get_y() + barsHigh[index].get_height()/2.
            # bad hack to compensate for shifted text in case of subscript
            if al.finalstate==None:
                bar_string = ""
            else:
#                if ( '$' in al.finalstate ) and ( '_' in al.finalstate ):
#                    yloc -= 0.1*barsHigh[index].get_height()
#                bar_string = r"$\bf{"+al.finalstate+":}$ "+Pas_Label
                bar_string = Pas_Label + r" ($\bf{"+al.finalstate+"}$)"
                if cadi:
                    arxiv_url = ''
                else:
                    arxiv_url = r'https://arxiv.org/abs/' + Pas_Label
            
            bar_text = ax.text(xloc, yloc, bar_string, horizontalalignment='left',
                               verticalalignment='center', color=desc_text_color,
                               clip_on=True, size=0.7*bar_height_points, url=arxiv_url, 
                               bbox = dict(color='w', alpha=0.01, url=arxiv_url))
            bar_texts.append(bar_text)

            bar_header = ax.text(0.048, yloc, r""+al.header+"", horizontalalignment='left',
                                verticalalignment='center', color='black',
                                transform = transFD,
                                clip_on=False, size=0.7*bar_height_points)
            bar_texts.append(bar_header)
            
            limstring = "%g" % (self.bar_vhighs[index])
            bar_limit = ax.text(xloclim, yloc, limstring, horizontalalignment='right',
                                verticalalignment='center', color=desc_text_color,
                                clip_on=True, size=0.7*bar_height_points)
            bar_texts.append(bar_limit)


            index += 1
        return ax

