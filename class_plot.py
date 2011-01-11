from class_curve import Curve
class Plot:
	"""
	Holds Curve Data
	"""
	def __init__(self, name = None):
		self._name		= name
		self._curves	= {}

	def __str__(self):
		ret_str	=	"plot '%s' - %d curves\n" % (self._name, len(self._curves))

		for n in self._curves:
			ret_str += "%s\t " % (n)
		
		return ret_str

	def addCurve(self, curve):
		self._curves[curve.getName()]	=	curve


#test
if __name__ == '__main__':
	p = Plot()
	c	=	Curve("Sup")
	c.addDataPoint((0,1,0))
	c.addDataPoint((0,1,0))
	c.addDataPoint((1,1,4))
	c.addDataPoint((2,4,2))
	
	p.addCurve(c)
	

	print c
	print p