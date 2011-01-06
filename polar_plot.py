from PyQt4 import QtCore                													#QT Core
from numpy import arange																	#For Arrange, etc.
from util_functions import rangeConvert	        											#my library of conversion functions and useful stuff
import pylab as p                       													#imports pylab, which provides interactivity features for matplotlib stuff
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas            #use a QT Backend
from matplotlib.pyplot import figure, show, rc, grid    									#various pyplot imports
import math   				              													#for sine wave generation and other fun math stuff like pi

class PolarPlot(FigureCanvas):
    """
    Defines a polar plot that does plots IR sensor as needed
    """
    def __init__(self, parent, *args):
        rc('grid', )
        rc('xtick', labelsize=10)
        rc('ytick', labelsize=10)
        self.width, self.height = matplotlib.rcParams['figure.figsize']
        self.size = min(self.width, self.height)
        self.fig = figure(figsize=(self.size, self.size))

        FigureCanvas.__init__(self, self.fig,*args)
        self.setParent(parent)

        self.ax = self.fig.add_axes([0.1, 0.07, 0.8, 0.8], polar=True)#, axisbg='#d5de9c')
        self.fig.suptitle('Range vs Angle', fontsize=15,horizontalalignment = 'center')
        self.r = [0]*54
        self.theta = arange(0, math.pi, math.pi/54)

        self.line = self.ax.plot(self.theta, self.r, 'bo', self.theta, self.r,'k', markerfacecolor='green',  lw=1, animated=True)
        self.line[0].set_ydata(self.r)
        self.line[1].set_ydata(self.r)    
        self.background = self.copy_from_bbox(self.ax.bbox)
        self.mpl_connect('draw_event', self.update_background)

        self.ax.set_rmax(160)
        self.ax.set_rmin(10)

        grid(True)

    def update_background(self,event):
        """
        Update the background buffer
        """
        self.background = self.copy_from_bbox(self.ax.bbox)           

    @QtCore.pyqtSlot(int,int)
    def polarUpdate(self, value, theta):
        """
        Updates the plot and redraws it
        """
        
        self.restore_region(self.background)
        if theta < 54 and theta >= 0:
            self.r[53-theta] = rangeConvert(value,0,"cm") #reverse the theta becase of the way the polar-plot works
        
        self.line[0].set_ydata(self.r)
        self.line[1].set_ydata(self.r)
        
        self.ax.draw_artist(self.line[0])
        self.ax.draw_artist(self.line[1])
        
        self.blit(self.ax.bbox)        
