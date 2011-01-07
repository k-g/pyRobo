import serial                       #for serial communication
import sys                          #This gets the commandline stuff for us
import threading, time              #for threads, and delays
import exceptions                   #for handling the standard array of crap that ails this file
from collections import deque       #for saving incoming serial data as a queue
import random                       #for wave generating that is a little more interesting
import math                         #for sine wave generation and other fun math like pi
import numpy                        #obviously needed for randomness, list generation, etc.

from util_functions import *        #my library of conversion functions and useful stuff
from strip_chart import *           #pyQWT strip chart
from polar_plot import *            #polar plot

from serial_threads import *

#global variables
t_thread = 0
g_thread = 0



@QtCore.pyqtSlot(int,int)
def updatePlots(value,theta):
    """
    The slot that updates local plots when new data arrives
    """
    global plot_update_signal_wrappers
    for sig in plot_update_signal_wrappers:
        sig.go(value,theta)




def make():
    """
    Setup the GUI, and plots
    """
    global plot_update_signal_wrappers

    #setup strip chart    
    stripWidget = Qt.QWidget()
    
    stripChart = StripChart(stripWidget)
    stripChart.setTitle("Range vs Time")
    stripChart.setMargin(5)

    stripLayout = Qt.QVBoxLayout(stripWidget)
    stripLayout.addWidget(stripChart)

    #setup polar plot
    polarWidget = Qt.QWidget()
   
    polarPlot = PolarPlot(polarWidget)
    polarLayout = Qt.QVBoxLayout(polarWidget)
    polarLayout.addWidget(polarPlot)
    
    #set sizes
    stripWidget.resize(600, 400)
    polarWidget.resize(600,600)

    #setup main window
    windowWidget = Qt.QWidget()
    windowLayout = Qt.QVBoxLayout()
    windowWidget.setLayout(windowLayout)
    windowLayout.addWidget(stripWidget)
    windowLayout.addWidget(polarWidget)
    windowWidget.setWindowTitle("IR Range")
    windowWidget.show()

    #plots to update when we get new values from the serial monitor
    plot_update_signal_wrappers = []
    plot_update_signal_wrappers.append(SigWrapper(stripChart.updatePlot))
    plot_update_signal_wrappers.append(SigWrapper(polarPlot.polarUpdate))
    return stripWidget,   polarWidget, windowWidget     



def stop_threads():
    """
    Stop threads from running
    """
    
    #send threads kill signal
    setAlive(0)

    #wait for them to halt
    try:
        g_thread.join()
        t_thread.join()
    except AttributeError:
        pass

#main program
def main(args):
    """
    Setup threads and serial 
    """
    
    global t_thread, g_thread
    
    print("Running")

    
    #make the window
    app         = Qt.QApplication(args)
    port_names  =    enumerateSerialPorts()
    strip,polar,window = make()
    
    #signal to threads 
    setAlive(1)
    t_thread    = openTelemetryThread("COM6",38400, alert_function=updatePlots)
    g_thread    = openGeneratorThread('COM9',38400)
    
    #detect when we're shutting down and send threads the kill signal
    app.aboutToQuit.connect(stop_threads)    
    
    #close when qtapp closes
    sys.exit(app.exec_())  


# Admire!
if __name__ == '__main__':
    main(sys.argv)
    