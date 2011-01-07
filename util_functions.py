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
    Converts an 8-bit integer number to a 2-digit hex representation
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
            output = 10000 /(measurement + 42) - 20.42
        else:
            #use calculation 2 for 20-84 cm
            output = 16667 /(measurement + 128.33) - 5.42
    
        if output > 150:
            output = 150
        elif output < 20:
            output = 20
    
    #type is short range sensor
    elif type == 1: 
        output = 1111.11 /(measurement + 4.56) - 1
        if output > 40:
            output = 40
        elif output < 1:
            output = 0

    if units == "in":
        output = output / 2.54
    
    return math.floor(output)