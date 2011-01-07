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

#global variables
isAlive = 0
telemetryPause = 0;
t_thread = 0
g_thread = 0

def enumerateSerialPorts(announce=1):
    """
    Will search for the first 256 ports and return the ports
    """
    port_counter = 0
    port_list    = []
    while port_counter < 256:
        try:
            s = serial.Serial(port_counter)
            port_list.append(s.portstr)
            if announce:            
                print("Found port %s" % (s.portstr));      
        except serial.SerialException:
            pass
        finally:
            port_counter += 1;
            
    return port_list
    


def serialMonitor(serial_obj, alert_function):
    """
    The actual serial Thread
    """
    global isAlive
    data=""
    dataList = deque([0,0,0,0,0,0,0,0,0,0,0,0])
    sig = SigWrapper(alert_function)
    
    while isAlive:
        try:
            the_new_val    =     serial_obj.read(1)
            data = data +      the_new_val        # read one, blocking
            dataList.append(the_new_val)  
            dataList.popleft()
                            
            
            if(dataList[0]=='+' and dataList[1]=='$'):
                try:
                    adc_reading = int(dataList[2],16)*16 + int(dataList[3],16)
                    angle_reading = int(dataList[4],16)*16 + int(dataList[5],16)
                    angle_theta = (angle_reading-21)*(180/(75-21))
                    sig.go(adc_reading, angle_reading)                    
                except ValueError, e:
                    pass
                    

        except serial.SerialException, e:
            print("Serial Thread Exception:", e)


def openTelemetryThread(port_name, baud_rate, alert_function):
    """
    Opens a thread with the given arguments that monitors serial comms and the window to draw to
    """
    try:
        #serial
        serial_obj=serial.Serial(
                 port=port_name,
                 baudrate=baud_rate,           #baudrate
                 bytesize=serial.EIGHTBITS,    #number of databits
                 parity=serial.PARITY_NONE,    #enable parity checking
                 stopbits=serial.STOPBITS_ONE, #number of stopbits
                 timeout=None,                 #set a timeout value, None for waiting forever
                 xonxoff=0,                    #enable software flow control
                 rtscts=0,                     #enable RTS/CTS flow control
                 )
        
        serial_obj.close()
        serial_obj.open()
        serial_obj.flushInput()
        serial_obj.flushOutput()
        #thread
        telemetry_thread = threading.Thread(target = serialMonitor, name = "SerialMonitorThread", args=(serial_obj,alert_function))

        #telemetry_thread.setDaemon(1)    #close with application

        telemetry_thread.start()
        
        return telemetry_thread 

    except serial.SerialException, e:
        print("Could not open port %s: %s" % (port_name, e))
    except RuntimeError, e:
        print("Runtime error: %s" (e))



def error_calc(reference, secondary):
    """
    Accepts 2 slices of an array and it's time-shifted rotation.
    These arrays must be the same length
    """
    error = 0
    for i in range(len(reference)):
        print "\t",reference
        print "\t",secondary
        print "\t-"*5
        error += abs(reference[i] - secondary[i])


    return error


def find_angle(reference, secondary):
    """
    Finds the best guess for rotation based on the error, then returns the guessed angle we rotated.
    """
    
    #these 2 must be even numbers th
    window_width    =   16               #width of search space. larger = slower, more accurate
    offset_width    =   20              #amount of side-to-side oscillation. lower = faster, less accurate
    
    center          =   26              #center of rotation
    
    rad_inc         =   math.pi / 54    #used for determining angles
    angle_errors    =   {}              #map offset_angle => error

    #setup reference window
    ref_start   =   center - (window_width/2)
    ref_end     =   ref_start + window_width
    ref_window  =   reference[ref_start:ref_end]        #reference window to use

    #setup loop
    smallest_error   =   255                              #keep track of the smallest error we see
    closest_angle   =   0                              #track the biggest error's angle
    nearest_offset  =   0

    for o in range(offset_width):
        relative_offset     =   (o-offset_width/2)+1        #offset, relative to "center" to use, in array indices
        angle               =   (rad_inc * 180/math.pi) * relative_offset #convert the index offset to degrees
        
        secondary_start     =   center  + relative_offset - window_width/2 #- (offset_width/2) + o

        print secondary_start, secondary[secondary_start], relative_offset
        secondary_end       =   secondary_start + window_width
        secondary_window    =   secondary[secondary_start:secondary_end]

        angle_errors[str(angle)] = error_calc(ref_window, secondary_window)
        if angle_errors[str(angle)] < smallest_error:
            smallest_error   =   angle_errors[str(angle)]
            closest_angle   =   angle
            nearest_offset  =   relative_offset
             

    print angle_errors
    


    return "Angle: ", closest_angle, "Offset: ", nearest_offset



def generate_test_readings(shift_indices, size=80):
    """
    Returns a pair of readings. One is shifted and noisy
    """
    shift_size  =   -shift_indices           
    start       =   numpy.random.random_integers(80, 160,  size=(size,))    #simulated measurement

    start[40]   =   27      #simulated 'spike' to help track on chart

    end         =   (start[:]+numpy.random.randint(-10,10, size=(size,)))   #simulated noisey second measurement

    readings    =   start[10:-10]                                           #take slices
    readings2   =   end[10+shift_size:-10+shift_size]                       #take shifted slices

    return readings.tolist(), readings2.tolist()


def serialGenerate(serial_obj):
    """
    The generator thread
    """
    global isAlive
    
    rad_inc = math.pi / 54
    loops   = 2
    l= 0
    while isAlive:
        try:

            readings, readings2 = generate_test_readings(-9)
                     
            
            while l < loops:
                count_inc   =   0
                radians = 0.0

                while count_inc  < 54:
                    time.sleep(0.02)
                    for character in "+$":
                        serial_obj.write(character)
                    
                    radians += rad_inc;
                    if radians > (2 * math.pi):
                        radians = 0.0
                                    
                    #run twice
                    if l == 0:
                        some_num = int(readings[count_inc])#int(random.randint(0, 5) + 120*(1 + math.sin(radians)))
                    else:
                        some_num = int(readings2[count_inc])#int(random.randint(0, 5) + 120*(1 + math.sin(radians)))


                    serial_obj.write(num2hex(some_num))
                    serial_obj.write(num2hex(count_inc))

                    count_inc += 1
                
                l += 1            
            
            isAlive = 0

            print find_angle(readings, readings2)

            break;

        except exceptions.AttributeError, e:
            pass    #most likely came during interpreter shutdown 
            #raise e               
        except serial.SerialException, e:
            print("Serial Thread Exception:", e)
        except serial.SerialTimeoutException, e:
            print("Serial Thread Timeout Exception:", e)
           

def openGeneratorThread(port_name, baud_rate):
    """
    Opens a thread with the given arguments that creates serial comms
    """
    try:
        #serial
        serial_obj=serial.Serial(
                 port=port_name,
                 baudrate=baud_rate,        #baudrate
                 bytesize=serial.EIGHTBITS,    #number of databits
                 parity=serial.PARITY_NONE,    #enable parity checking
                 stopbits=serial.STOPBITS_ONE, #number of stopbits
                 timeout=None,             #set a timeout value, None for waiting forever
                 xonxoff=0,             #enable software flow control
                 rtscts=0,              #enable RTS/CTS flow control
                 )
        serial_obj.close()                 
        serial_obj.open()
        serial_obj.flushInput()
        serial_obj.flushOutput()
        #thread
        generator_thread = threading.Thread(target = serialGenerate, name = "SerialGenerateThread",args=(serial_obj,))

        #generator_thread.setDaemon(1)    #close with application

        generator_thread.start()
        return generator_thread        
        
    except exceptions.AttributeError, e:
        pass    #most likely came during interpreter shutdown  
    except serial.SerialException, e:
        print("Could not open port %s: %s" (port_name, e))
    except RuntimeError, e:
        print("Runtime error: %s" (e))


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
    
    stripWidget = Qt.QWidget()
   
    
    stripChart = StripChart(stripWidget)
    stripChart.setTitle("Range vs Time")
    stripChart.setMargin(5)

    stripLayout = Qt.QVBoxLayout(stripWidget)
    stripLayout.addWidget(stripChart)
   

    polarWidget = Qt.QWidget()
   

    polarPlot = PolarPlot(polarWidget)

    polarLayout = Qt.QVBoxLayout(polarWidget)
    polarLayout.addWidget(polarPlot)
    
    stripWidget.resize(600, 400)
    polarWidget.resize(600,600)

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
    global isAlive
    isAlive = 0         #signal to threads it's time to close
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
    
    global isAlive
    global telemetryPause
    global t_thread, g_thread
    
    print("Running")

    
    #make the window
    app         = Qt.QApplication(args)
    port_names  =    enumerateSerialPorts()
    strip,polar,window = make()
    app.aboutToQuit.connect(stop_threads)

    #signal to threads 
    isAlive     = 1
    t_thread    = openTelemetryThread("COM6",38400, alert_function=updatePlots)
    g_thread    = openGeneratorThread('COM9',38400)
    
    #close when qtapp closes
    sys.exit(app.exec_())  


# Admire!
if __name__ == '__main__':
    main(sys.argv)
    