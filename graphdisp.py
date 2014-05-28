from pyserdisp import Serdisp
from textrenderer import Font
import Image

class GraphDisp(Serdisp):
	def __init__(self, device, model, options = ""):
		self.disp = Serdisp.__init__(self, device, model, options)
		self.font = Font("DroidSans.ttf", 12)

	def __enter__(self):
		Serdisp.__enter__(self)
		return self

	def __exit__(self, type, value, traceback):
		Serdisp.__exit__(self, type, value, traceback)

	def drawPixmap(self, path):
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

	def drawText(self, textpos, text, colour = Serdisp.BLACK):
		bitmap = self.font.render_text(text)
		for y in range(bitmap.height):
			for x in range(bitmap.width):
				pixpos = [textpos[0] + x, textpos[1] + y]
				#print x, y, bitmap.pixels[x+y*bitmap.width]
				pixBit = (1 - bitmap.pixels[x + y * bitmap.width])
				#print pixBit, colour, pixCol, pixBit * colour[0]
				Serdisp.setGrey(self, pixpos, pixBit * 255)
