import serial                       #for serial communication
import sys                          #This gets the commandline stuff for us
import threading, time              #for threads, and delays
import exceptions                   #for handling the standard array of crap that ails this file
#from collections import deque       #for saving incoming serial data as a queue
#import random                       #for wave generating that is a little more interesting
#import math                         #for sine wave generation and other fun math like pi
import numpy                        #obviously needed for randomness, list generation, etc.

from util_functions import *        #my library of conversion functions and useful stuff
from strip_chart import *           #pyQWT strip chart
from polar_plot import *            #polar plot

from serial_threads import *

#global variables
t_thread = 0
g_thread = 0
updates = 0                    #counts our packets
readings1 = numpy.zeros(54)
readings2 = numpy.zeros(54)    #stores new and old data
delta    =    None

@QtCore.pyqtSlot(int,int)
def updatePlots(value,theta):
    """
    The slot that updates local plots when new data arrives
    """
   # global readings1, readings2, delta    
    
    
   
    #update buffers
    readings1[theta]   =      readings2[theta]
    print readings1[theta]

    readings2[theta]    =     value
    print readings2[theta]    
    
    print theta
    
    if theta == 53:
        #print readings1, readings2
        angle_str = str(find_angle(readings1, readings2))
       # readings1 = readings2[:]        #deep copy on finish
        delta.setText(angle_str)
     

    
    
    global plot_update_signal_wrappers
    for sig in plot_update_signal_wrappers:
        sig.go(value,theta)


def make():
    """
    Setup the GUI, and plots
    """
    global plot_update_signal_wrappers, delta

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
    
    #text box for output
    label=Qt.QLabel("Delta Angle")
    delta=Qt.QLineEdit("0.0")
    label.setBuddy(delta)
    
    #set sizes
    stripWidget.resize(600, 400)
    polarWidget.resize(600, 600)

    #setup main window
    windowWidget = Qt.QWidget()
    windowLayout = Qt.QVBoxLayout()
    windowWidget.setLayout(windowLayout)
    windowLayout.addWidget(stripWidget)
    windowLayout.addWidget(polarWidget)
    windowLayout.addWidget(label)
    windowLayout.addWidget(delta)    
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
    