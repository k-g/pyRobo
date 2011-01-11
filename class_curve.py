from PyQt4 import QtCore                #QT Core
class Curve:
	"""
	Holds data for a curve and a few properties about it
	"""
	def __init__(self, name = None, filter_function = None, max_length = 60):
		self._name			=	name			#the name of the curve. Can be descriptive.
		self._filter		=	filter_function	#used to process incoming data
		
		#default parameters
		self._max_length	=	max_length		#number of entries allowed max
		self._data			=	[]				#list mapping primary index(x) -> ( tuple(y) , of remaining(z), dimensions(a))
		
		#default processing
		if filter_function is None:	self._filter = self._default_filter


	def _default_filter(self, val):
		"""
		Checks for bad number values
		"""
		for k in val:
			if not str(k).isdigit():
				raise TypeError("%s is NaN"%str(val))

		return val
	
	def __str__(self):
		"""
		Returns a list of points and indices
		"""
		ret_str = "dataset '%s' - %d items\n" % (self._name,len(self._data))
		for k in range(len(self._data)):
			ret_str += "%d -> %s\n" %(k, str(self._data[k]))

		return ret_str

	@QtCore.pyqtSlot(tuple)		
	def addDataPoint(self,	val):
		"""
		Add data to the queue and filter
		"""
		if(len(self._data) > self._max_length):
			self._data	=	self._data[:-1]

		self._data.append( self._filter(val) )

	def unzipData(self):
		"""
		returns X,Y tuple of data
		"""
		x,y = zip(*(self.getData()))
		return list(x),list(y)

	def getData(self):
		"""
		Return data set
		"""
		return self._data
	
	def getName(self):
		"""
		Return a name
		"""
		return self._name


#test
if __name__ == '__main__':
    
    c	=	Curve()
    c.addDataPoint((0,0))
    c.addDataPoint((3,0))
    c.addDataPoint((0,2))
    c.addDataPoint((0,0))
    print c
    print c.unzipData()