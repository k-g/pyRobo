from PyQt4 import Qt                    #Other Qt stuff
from PyQt4 import QtCore                #QT Core
import PyQt4.Qwt5 as Qwt                #Qwt graphing
from PyQt4.Qwt5.anynumpy import *       #imports the latest numpy
from util_functions import rangeConvert

from class_curve import Curve

class StripChartLine(Qwt.QwtPlotCurve):
    """
    Represents a curve or line on a strip chart
    """
    def __init__(self, *args):
        Qwt.QwtPlotCurve.__init__(self, *args)
        self.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
        pen = Qt.QPen(Qt.QColor('limegreen'))
        pen.setWidth(2)
        self.setPen(pen)

    def setColor(self, color):
        pen = Qt.QColor(color)
        self.setPen(pen)


class StripChart(Qwt.QwtPlot):
    """
    This is a strip chart that measures something
    """
    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)

        self.MAX_ENTRIES = 60
        self.oldData = False
        
        self.timeData = 1.0 * arange(self.MAX_ENTRIES-1, -1, -1)
        self.timer = Qt.QTime()
        self.timer.restart()
        
        self.setAutoReplot(False)

        self.plotLayout().setAlignCanvasToScales(True)

        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time")

        #time shifted to EST
        self.setAxisScaleDraw(
            Qwt.QwtPlot.xBottom, TimeScaleDraw((Qt.QTime().currentTime().addSecs(-10*3600-30*60))))

        self.setAxisScale(Qwt.QwtPlot.xBottom, 0, self.MAX_ENTRIES)

        self.setAxisLabelAlignment(Qwt.QwtPlot.xBottom, Qt.Qt.AlignLeft | Qt.Qt.AlignBottom)

        self.setAxisTitle(Qwt.QwtPlot.yLeft, "Range (cm)")

        self.setAxisScale(Qwt.QwtPlot.yLeft, 10, 160)

        self.setCanvasBackground(Qt.Qt.black)

        self.curve = StripChartLine()
        self.curve.attach(self)

        self.data = zeros(self.MAX_ENTRIES, Float)

        self.replot()

    # __init__()
    @QtCore.pyqtSlot(int,int)
    def updatePlot(self, newValue, angle):
        """
        Add a new value to this chart, somewhere. Angle is unused atm
        """
        self.data[1:] = self.data[0:-1]

        self.data[0] = rangeConvert(newValue,0,"cm")
        
        self.timeData += self.timer.elapsed()*0.001 #scale to MS (timer.elapsed returns an int-number of MS)

        self.timer.restart()
        
        #rescale x axis
        self.setAxisScale(
            Qwt.QwtPlot.xBottom, self.timeData[-1], self.timeData[0])
        
        #update the data that we plot
        self.curve.setData(self.timeData, self.data)
        self.replot()


class TimeScaleDraw(Qwt.QwtScaleDraw):
    """
    Used to create an X-axis based on real time
    """
    def __init__(self, baseTime, *args):
        Qwt.QwtScaleDraw.__init__(self, *args)
        self.baseTime = baseTime

    def label(self, value):
        upTime = self.baseTime.addSecs( int(value))
        return Qwt.QwtText(upTime.toString("h:mm:ss ap"))