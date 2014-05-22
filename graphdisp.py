from pyserdisp import Serdisp
import Image

class GraphDisp(Serdisp):
	def __init__(self, device, model, options = ""):
		self.disp = Serdisp.__init__(self, device, model, options)

	def __enter__(self):
		Serdisp.__enter__(self)
		return self

	def __exit__(self, type, value, traceback):
		Serdisp.__exit__(self, type, value, traceback)

	def showPixmap(self, path):
		img = None
		try:
			img = Image.open(path)
			img.load()
		except IOError:
			print "Couldn't open", path

		# TODO only if necessary				
		img.convert("1") # Convert to black/white mode
		bg = list(img.getdata())
		width, height = img.size
		bg = [bg[i * width:(i + 1) * width] for i in xrange(height)]

		for x in range(width):
			for y in range(height):
				Serdisp.setColour(self, [x, y], bg[y][x])

