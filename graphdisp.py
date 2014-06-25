from pyserdisp import Serdisp
from textrenderer import Font
import Image

class GraphDisp:
	def __init__(self, device, model, options = ""):
		self.serdisp = Serdisp(device, model, options)
		self.font = Font("/home/pi/.xbmc/addons/xbmcdisp/DroidSans.ttf", 12)

	def __enter__(self):
		self.serdisp.__enter__()
		return self

	def __exit__(self, type, value, traceback):
		self.serdisp.__exit__(type, value, traceback)


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

	def drawText(self, textpos, text, colour = Serdisp.BLACK, halign = None, valign = None):
		"""
		Alignment:
		halign can be one of ["left", "center", "right", None]
		valign can be one of ["top", "center", "bottom", None]
		If an alignment is specified, the corresponding textpos coordinate
		is interpreted as offset from that display edge or ignored for "center".
		"""
		if not len(textpos) == 2:
			raise ValueError("textpos must consist of 2 coordinates")

		bitmap = self.font.render_text(text)

		if halign == "left":
			pass
		elif halign == "center":
			textpos[0] = (self.disp.getWidth() / 2.0) - (bitmap.width / 2.0)
		elif halign == "right":
			textpos[0] = self.disp.getWidth() - bitmap.width - textpos[0]
		if valign == "top":
			pass
		elif valign == "center":
			textpos[1] = (self.disp.getHeight() / 2.0) - (bitmap.height / 2.0)
		elif valign == "bottom":
			textpos[1] = self.disp.getHeight() - bitmap.height - textpos[1]

		for y in range(bitmap.height):
			for x in range(bitmap.width):
				pixpos = [textpos[0] + x, textpos[1] + y]
				pixBit = (1 - bitmap.pixels[x + y * bitmap.width])
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
