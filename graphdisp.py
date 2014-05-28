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

	def drawProgressBar(self, pos, size, state):
		if state < 0:
			state = 0
		if state > 1:
			state = 1

		if pos[0] < 0 or pos[1] < 0:
			raise ValueError("pos must not be negative")
		if size[0] < 1 or size[1] < 1:
			raise ValueError("size must be greater than 1")

		if size[0] >= 3 and size[1] >= 3:
			# draw a border
			for x in range(size[0] + 1):
				Serdisp.setGrey(self, [pos[0] + x, pos[1]], 0)
				Serdisp.setGrey(self, [pos[0] + x, pos[1] + size[1]], 0)
			for y in range(size[1] + 1):
				Serdisp.setGrey(self, [pos[0], pos[1] + y], 0)
				Serdisp.setGrey(self, [pos[0] + size[0], pos[1] + y], 0)

		# draw the status bar "content"
		contentWidth = round(state * float(size[0] + 1))
		for x in range(contentWidth):
			for y in range(size[1] + 1):
				Serdisp.setGrey(self, [pos[0] + x, pos[1] + y], 0)
