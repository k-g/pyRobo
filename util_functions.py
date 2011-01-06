import math                 #for sine wave generation and other fun math
#from PyQt4 import Qt                    #Other Qt stuff
from PyQt4 import QtCore                #QT Core

class SigWrapper(QtCore.QObject):
    """
    This signal wrapper is used to send out serial values to different graphs, in different threads, and stuff
    """
    bat_symbol = QtCore.pyqtSignal(int,int)
    def __init__(self, function):
        """
        Pass this the name of the function you want to call when you call 'go'
        """
        QtCore.QObject.__init__(self)
        self.bat_symbol.connect(function)

    def go(self,value,angle):
        """
        Raise the signal
        """
        self.bat_symbol.emit(value,angle)


def num2hex(some_val):
    """
    Converts an integer number to a 2-digit hex representation
    """
    the_hex = ""
    if some_val < 16 :
        the_hex += "0"
    if some_val > 255:
        raise ValueError, ""
    the_hex += (hex(some_val).replace("0x",""))
    return the_hex


def rangeConvert(measurement, type = 0, units = "cm"):
    """
    Converts ADC output to some other unit form depending on type of sensor
    """
    
    #default output for unknown sensor types
    output = measurement
    
    #type is long range sensor      
    if type == 0:
        
        if measurement > 53: 
            #use calculation 1 for 85-150cm
            #output = 10000 /((256/3.3) * (measurement*3.0/256) + 42) - 20.42
            #output = 10000 /(measurement + 42) - 20.42
            ##  output = (1/.00001)/(measurement + (0.0042/0.0001))-20.42
            output = 10000 /(measurement + 42) - 20.42
        else:
            #use calculation 2 for 20-84 cm
            #output = 16667 /((256/3.3) * (measurement*3.0/256) + 128.33) - 5.42
            #output = 16667 /(measurement + 128.33) - 5.42
            ##  output = (1/0.00006)/(measurement + (0.0077/0.00006)) - 5.42
            output = 16667 /(measurement + 128.33) - 5.42
    
        if output > 150:
            output = 150
        elif output < 20:
            output = 20
    
    #type is short range sensor
    elif type == 1: 
        #output = 1111.11 /((256/3.3) * (measurement*3.0/256) + 4.56) - 1
        #output = 1111.11 /(measurement + 4.56) - 1
        ##  output = (1/.00009)/(measurement + (0.0041/0.0009))-1
        output = 1111.11 /(measurement + 4.56) - 1
        if output > 40:
            output = 40
        elif output < 1:
            output = 0
    
    # type is accelerometer X axis
    elif type == 2:
        if xInit ==  0:
            prevX = measurement
            xInit = 1
            
        if measurement == 0 and prevX == 255:
            xParse = prevX + 1
        elif measurement == 255 and prevX == 0:
            xParse = xParse - 1
        elif measurement > prevX:
            xParse = xParse + 1
        elif measurement < prevX:
            xParse = xParse - 1
            
        prevX = measurement
        output = xParse
        # output("Parsed X: %s" % str(output))
    
    # type is accelerometer Y axis
    elif type == 3:
        if yInit ==  0:
            prevY = measurement
            yInit = 1
            
        if measurement == 0 and prevY == 255:
            yParse = prevY + 1
        elif measurement == 255 and prevY == 0:
            yParse = yParse - 1
        elif measurement > prevY:
            yParse = yParse + 1
        elif measurement < prevY:
            yParse = yParse - 1
            
        prevY = measurement
        output = yParse
        # output("Parsed Y: %s" % str(output))
    
    # type is accelerometer Z axis
    elif type == 4:
        if zInit ==  0:
            prevZ = measurement
            zInit = 1
            
        if measurement == 0 and prevZ == 255:
            zParse = prevZ + 1
        elif measurement == 255 and prevZ == 0:
            zParse = zParse - 1
        elif measurement > prevZ:
            zParse = zParse + 1
        elif measurement < prevZ:
            zParse = zParse - 1
            
        prevZ = measurement
        output = zParse
        # output("Parsed Z: %s" % str(output))
    
    #capacitor voltage
    elif type == 5:
        if(measurement==0):
            return 0
        else:   
            output =  ((3.3*measurement)/256.0 * 4) * 10
            return round(output, 0)

    #solar voltage
    elif type == 6:
        if(measurement==0):
            return 0
        else:   
            output =  ((3.3*measurement)/256.0 * 4) * 10
            return round(output, 0)
    else:
        pass

    #output("Calculated range to be: %d" % math.floor(output))
    
    if units == "in":
        output = output / 2.54
    
    return math.floor(output)