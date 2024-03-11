# +
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import matplotlib
import math
import os
import numpy as np
from matplotlib.colors import LogNorm
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import healpy as hp
SPINE_COLOR = "#A9A9A9"#"grey"
TEXT_COLOR = "#333333" #https://colors.muz.li/color/a9a9a9

inches_per_pt = 1.0/72.27
sets = {"margin": {"size" : 157.91196 * inches_per_pt, "ms" : 3, "lw" : 1.} ,
         "main":  {"size" : 312.97867 * inches_per_pt, "ms" : 3, "lw" : 1.5} ,
         "full" :  {"size" : 508.44804 * inches_per_pt, "ms" : 4, "lw" : 1.5}}


class Latexify():
    
    def __init__(self,fig_width, ratio, typeKey = "margin", hpmap = False, kwargs = {}, GridSpec = {}):
        self.typeKey = typeKey
        self.set_sizes(fig_width, ratio) #set some globals regarding sizes
        
        self.latexify() #primary style config

        
        if bool(GridSpec): #complicated grid plots
            self.make_GridSpec(GridSpec)
            
        elif hpmap: 
            print("Call self.heatmap and self.plot_heatmap_grid (if you don't use the latter, the ticks will be wrong)")

        else:
            if bool(kwargs):
                self.fig, self.ax = plt.subplots(figsize=self.figsize,**kwargs)
            else:
                self.fig, self.ax = plt.subplots(figsize=self.figsize)
                

    def make_GridSpec(self, GridSpecDic):
        from matplotlib.gridspec import GridSpec
        print("Starting GridSpec plot, you have to define ax from self.gs")
        self.fig=plt.figure(figsize=[self.fig_width, self.fig_height])
        self.gs = GridSpec(**GridSpecDic) if isinstance(GridSpecDic, dict) else GridSpec(GridSpecDic[0],GridSpecDic[1])

    def set_sizes(self, fig_width, ratio):
        self.set_width = fig_width
        self.set_ratio = ratio
        try:
            scaling = sets[self.typeKey]["size"]
        except: 
            print("WARNING: Picture type ",self.typeKey," not in dictionary. Using default margin")
            scaling = sets[self.typeKey]["size"]
            
        topright_lw = 0.75 if self.typeKey in ["main", "full"] else 0.55
        self.gridkwargs = {"color" : "#595959", "ls" : '-', "lw" : topright_lw, "alpha" : 0.3}
        
        self.fig_width  = self.set_width*scaling
        self.fig_height = self.set_ratio*self.fig_width
        print(f"Picture type {self.typeKey}, size {self.fig_width} x {self.fig_height}")
        self.figsize = [self.fig_width, self.fig_height]

    def latexify(self):
        matplotlib.rc('axes',edgecolor="#595959")
        matplotlib.rc('text',usetex=True)
        #matplotlib.rc('text.latex', preamble=[r"\usepackage{color}", r"\usepackage{wasysym}", r"\usepackage{txfonts}"])
        self.params = {
              'backend': 'ps',
              #'text.latex.preamble': [r"\usepackage[scaled=.97,helvratio=.93,p,theoremfont]{newpxtext}"],
              'axes.labelsize': 8, # fontsize for x and y labels (was 10)
              'axes.titlesize': 8,
              'font.size':       8, # was 10
              'legend.fontsize': 7.5, # was 10
              'xtick.labelsize': 7.5,
              'ytick.labelsize': 7.5,
              'text.usetex': True,
              'pgf.texsystem': "pdflatex",
              'figure.figsize': [self.fig_width, self.fig_height],
              'font.family': 'serif',
              'font.serif': ['Palatino'],  # blank entries should cause plots to inherit fonts from the document
              'font.sans-serif': ['Helvetica'],
              'xtick.major.pad' : "0.5",
              'ytick.major.pad' : "0.5",
              'text.color' :  TEXT_COLOR,
              'axes.labelcolor' :  TEXT_COLOR,
              'xtick.color' :  TEXT_COLOR,
              'ytick.color' :  TEXT_COLOR,
              'axes.labelpad' : 1.,
            
            'lines.markersize' : sets[self.typeKey]["ms"],
            'lines.linewidth' : sets[self.typeKey]["lw"],
            'legend.fancybox': True,
            "text.latex.preamble": "\n".join([ # plots will use this preamble
                                        r"\usepackage[utf8]{inputenc}",
                                        r"\usepackage[T1]{fontenc}",
                                        r"\usepackage[separate-uncertainty=true]{siunitx}",
                                        r"\usepackage{tikz}",
                                        ])
            }

        
        matplotlib.rcParams.update(self.params)
        #matplotlib.style.use('tableau-colorblind10')
        matplotlib.style.use("seaborn-colorblind")
        


    def format_axes(self,ax, ax2,  grid = True,two_axes = False, log = None):
        if self.typeKey in ["main", "full"]:
            leftbottom_lw = 1.2
            topright_lw = 0.75
            ticklength = 3
        else:
            leftbottom_lw = 0.9
            topright_lw = 0.55
            ticklength = 1.5

        self.gridkwargs = {"color" : "#595959", "ls" : '-', "lw" : topright_lw, "alpha" : 0.3}
        if two_axes == False:
            for spine in ['top', 'right']:
                #ax.spines[spine].set_visible(False)
                ax.spines[spine].set_color(SPINE_COLOR)
                ax.spines[spine].set_linewidth(topright_lw)

            for spine in ['left', 'bottom']:
                ax.spines[spine].set_color(SPINE_COLOR)
                ax.spines[spine].set_linewidth(leftbottom_lw)
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
            i=0
            for axis in [ax.xaxis, ax.yaxis]:
                axis.set_tick_params(direction='out', color=SPINE_COLOR, length = ticklength)
                if i==0 and (log == 'x' or log == 'xy'):
                    axis.set_tick_params(direction='out', which = 'minor', color=SPINE_COLOR, length = ticklength)
                if i == 1 and (log == 'y' or log == 'xy'):
                    axis.set_tick_params(direction='out', which = 'minor', color=SPINE_COLOR, length = ticklength)
                i = i+1
            ax.set_axisbelow(False) 
            if grid:
                ax.grid(**self.gridkwargs)
            return ax
        else:
            for spine in ['top']:
                ax.spines[spine].set_color(SPINE_COLOR)
                ax.spines[spine].set_linewidth(topright_lw)
                ax2.spines[spine].set_visible(False)
            for spine in ['left', 'bottom']:
                ax.spines[spine].set_color(SPINE_COLOR)
                ax.spines[spine].set_linewidth(leftbottom_lw)
                ax2.spines[spine].set_visible(False)
            for spine in ['right']:
                ax.spines[spine].set_visible(False)
                ax2.spines[spine].set_color(SPINE_COLOR)
                ax2.spines[spine].set_linewidth(topright_lw)

            ax2.yaxis.set_ticks_position('right')

            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')

            for axis in [ax.xaxis, ax.yaxis, ax2.yaxis]:
                axis.set_tick_params(direction='out', color=SPINE_COLOR, length = ticklength)

            ax2.set_axisbelow(False)

            ax.set_axisbelow(False)
            if grid:
                ax2.grid(**self.gridkwargs)
            return ax, ax2

    def savefig(self,path,filename, pdf = True, dpi = 300, tight = True, bboxinchesTight = True):
        if not (os.path.exists(path)):
            os.makedirs(path)
        self.fig.set_size_inches(self.fig_width, self.fig_height)
        #self.fig.set_constrained_layout_pads(w_pad=0, h_pad=0)
        
        unDict = {"transparent" : True}
        filename = os.path.join(path, filename)
        if tight:
            plt.tight_layout(pad=0)
        if bboxinchesTight:
            unDict["bbox_inches"] = 'tight'
            
        plt.savefig(f'{filename}.png', dpi =  dpi, **unDict)
        if pdf:
            plt.savefig(f'{filename}.pdf',  **unDict)
                
                
        plt.show()
    #from https://git.rwth-aachen.de/astro/astrotools/-/blob/master/astrotools/skymap.py modified
    def heatmap(self, m, label='entries', xresolution = 800, projection = "mollweide", cmap = 'viridis', vmin = None, vmax = None,
               cbticks = None, colorbar = False, vcenter = None):
        
        yresolution = xresolution // 2
        theta = np.linspace(np.pi, 0, yresolution)
        phi = np.linspace(-np.pi, np.pi, xresolution)
        
        longitude = np.deg2rad(np.linspace(-180, 180, xresolution))
        latitude = np.deg2rad(np.linspace(-90, 90, yresolution))

        phi_grid, theta_grid = np.meshgrid(phi, theta)
        grid_pix = hp.ang2pix(hp.get_nside(m), theta_grid, phi_grid)

        if isinstance(cmap, str):
            cmap = plt.cm.get_cmap(cmap)
            
        finite = np.isfinite(m)
        self.vmin = vmin if vmin is not None else smart_round(np.min(m[finite]), upper_border=False)
        self.vmax = vmax if vmax is not None else smart_round(np.max(m[finite]), upper_border=True)
        
        cbticks = cbticks if cbticks is not None else [self.vmin, (self.vmin + self.vmax) / 2, self.vmax]
        if vcenter is not None:
            divnorm = mpl.colors.TwoSlopeNorm(vmin=self.vmin, vcenter=0., vmax=self.vmax) 
            cbticks[1] = 0
            
        else:
            divnorm = mpl.colors.TwoSlopeNorm(vmin=self.vmin, vcenter = (self.vmin + self.vmax) / 2, vmax=self.vmax)
        offset = np.mean(m)
        grid_map = m[grid_pix]

        self.fig = plt.figure(figsize = self.figsize)
        self.fig.add_subplot(111, projection=projection)
        # flip longitude to the astro convention
        # rasterized makes the map bitmap while the labels remain vectorial
        #image = plt.pcolormesh(longitude[::-1], latitude, grid_map, rasterized=True, vmin=vmin, vmax=vmax, cmap=cmap,
                              # edgecolor='face', shading='auto', **kwargs)
        #I DONT WANT ANY FLIP
        image = plt.pcolormesh(longitude, latitude, grid_map, rasterized=True, norm = divnorm,
                                cmap=cmap, edgecolor='face', shading='auto')#vmin= self.vmin, vmax=self.vmax,
        
        if colorbar:
            cb = self.fig.colorbar(image, ticks=cbticks, orientation='horizontal', 
                                   aspect=30, shrink=0.9, pad=0.05)
            cb.solids.set_edgecolor("face")
            cb.set_label(label)
            cb.ax.tick_params(axis='x', direction='out', size=2)
            self.cb = cb
            


    def plot_heatmap_grid(self, lat_ticks=None, lon_ticks=None, lon_grid=45, lat_grid=30, 
                          tickalpha = 0.5, xtickColor = "white", plotTicks = True):

        plt.gca().set_longitude_grid(lon_grid)
        plt.gca().set_latitude_grid(lat_grid)
        plt.gca().set_longitude_grid_ends(89)
        inLON = np.unique(np.append(-np.arange(0, 180, lon_grid),np.arange(0, 180, lon_grid)))
        inLAT = np.unique(np.append(-np.arange(0, 90, lat_grid),np.arange(0, 90, lat_grid)))

        lon_ticks = inLON if lon_ticks is None else lon_ticks
        
        xticks = []
        for lon in inLON:
            if lon in lon_ticks:
                xticks.append(r'%d$^{\circ}$' % lon)
            else:
                xticks.append(r'')
                
        yticks = []
        print(lat_ticks)
        for lat in inLAT:
            latT = 90-lat
            if lat_ticks is not None:
                if latT in lat_ticks:
                    yticks.append(r'%d$^{\circ}$' % latT)
                else:
                    yticks.append(r'')
            else:
                yticks.append(r'%d$^{\circ}$' % latT)

        plt.grid(**self.gridkwargs)
        plt.gca().set_xticklabels(xticks,alpha=tickalpha)
        plt.gca().tick_params(axis='x', colors= xtickColor)
        plt.gca().set_yticklabels(yticks)
        
        if not plotTicks:
            self.fig.axes[0].set_xticklabels([])
            self.fig.axes[0].set_yticklabels([])


# +

def smart_round(v, order=2, upper_border=True):
    """
    Rounds a value v such that it can be used e.g. for colorbars

    :param v: scalar value which should be rounded
    :type v: int, float
    :param upper_border: round such that the value can be used as an upper border of an interval, default=True
    :param order: number of digits to round to, default=2
    :return: rounded value
    :rtype: int, float

    This function has been tested on the following numbers (with all upper_border presented here):

    .. code-block:: python

        :linenos:
        >> from astrotools.skymap import smart_round
        >> smart_round(100000), smart_round(100000, upper_border=False)
        100000.0, 100000.0
        >> smart_round(100001), smart_round(100001, upper_border=False)
        101000.0, 100000.0
        >> smart_round(-100001), smart_round(-100001, upper_border=False)
        -100000.0, -100000.0
        >> smart_round(2.23), smart_round(2.23, upper_border=False)
        2.23, 2.23
        >> smart_round(2.230), smart_round(2.230, upper_border=False)
        2.23, 2.23
        >> smart_round(2.231), smart_round(2.231, upper_border=False)
        2.24, 2.23
        >> smart_round(-2.230), smart_round(-2.230, upper_border=False)
        -2.23, -2.23
        >> smart_round(-2.231), smart_round(-2.231, upper_border=False)
        -2.23, -2.24
        >> smart_round(0.930001), smart_round(0.930001, upper_border=False)
        0.94, 0.93
        >> smart_round(-0.930001), smart_round(-0.930001, upper_border=False)
        -0.93, -0.94
    """
    if v == 0:
        return 0
    o = np.log10(np.fabs(v))
    f = 10 ** (-int(o) + order)
    if upper_border:
        return np.ceil(v * f) / f
    return np.floor(v * f) / f


# -





