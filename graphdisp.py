from pyserdisp import Serdisp
from textrenderer import Font
import Image

class GraphDisp:
	def __init__(self, device, model, options = ""):
		self.serdisp = Serdisp(device, model, options)
		self.font = "/home/pi/.xbmc/addons/xbmcdisp/DroidSans.ttf"
		self.nextFrame = self.setupNewFrame()
		self.prevFrame = self.setupNewFrame()

	def __enter__(self):
		self.serdisp.__enter__()
		return self

	def __exit__(self, type, value, traceback):
		self.serdisp.clear()
		self.serdisp.__exit__(type, value, traceback)

	def setupNewFrame(self):
		column = [(255, 255, 255, 255) for x in xrange(self.serdisp.getHeight())]
		return [list(column) for x in xrange(self.serdisp.getWidth())]

	def flip(self):
		for x in xrange(self.serdisp.getWidth()):
			for y in xrange(self.serdisp.getHeight()):
				oldPix = self.prevFrame[x][y]
				newPix = self.nextFrame[x][y]
				if (not oldPix[0] == newPix[0] or
					not oldPix[1] == newPix[1] or
					not oldPix[2] == newPix[2]):
					self.serdisp.setColour([x,y], self.nextFrame[x][y])
					#self.prevFrame[x][y] = self.serdisp.WHITE

		self.serdisp.update()
		#tmp = self.prevFrame
		self.prevFrame = self.nextFrame
		#self.nextFrame = tmp
		self.nextFrame = self.setupNewFrame()

	def drawPixel(self, pos, value):
		"""
		Expects coordinates and an ARGB pixel.
		"""
		if len(value) == 1:
			value = (255, value[0], value[0], value[0])
		elif len(value) == 3:
			value = (255, value[0], value[1], value[2])

		try:
			if not self.nextFrame[pos[0]][pos[1]][0] == 0:
				self.nextFrame[pos[0]][pos[1]] = value
		except IndexError:
			#print "Overdraw:", pos[0], pos[1]
			pass

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
				self.drawPixel((x, y), bg[y][x])

	def drawText(self, textpos, text, colour = Serdisp.BLACK, halign = None, valign = None, size = 12):
		"""
		Alignment:
		halign can be one of ["left", "center", "right", None]
		valign can be one of ["top", "center", "bottom", None]
		If an alignment is specified, the corresponding textpos coordinate
		is interpreted as offset from that display edge or ignored for "center".
		"""
		if not len(textpos) == 2:
			raise ValueError("textpos must consist of 2 coordinates")

		font = Font(self.font, size)
		bitmap = font.render_text(text)

		if halign == "left":
			pass
		elif halign == "center":
			textpos[0] = int(round((self.serdisp.getWidth() / 2.0) - (bitmap.width / 2.0)))
		elif halign == "right":
			textpos[0] = self.serdisp.getWidth() - bitmap.width - textpos[0]
		if valign == "top":
			pass
		elif valign == "center":
			textpos[1] = int(round((self.serdisp.getHeight() / 2.0) - (bitmap.height / 2.0)))
		elif valign == "bottom":
			textpos[1] = self.serdisp.getHeight() - bitmap.height - textpos[1]

		for y in xrange(min(bitmap.height, self.serdisp.getHeight())):
			for x in xrange(min(bitmap.width, self.serdisp.getWidth())):
				pixpos = [textpos[0] + x, textpos[1] + y]
				pixel = (1 - bitmap.pixels[x + y * bitmap.width]) * 255
				self.drawPixel(pixpos, (255, pixel, pixel, pixel))

	def drawProgressBar(self, pos, size, state, colour = (255, 0, 0, 0)):
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
			for x in range(size[0]):
				self.drawPixel((pos[0] + x, pos[1]), colour)
				self.drawPixel((pos[0] + x, pos[1] + size[1] - 1), colour)
			for y in range(size[1] - 1):
				self.drawPixel((pos[0], pos[1] + y), colour)
				self.drawPixel((pos[0] + size[0] - 1, pos[1] + y), colour)

		# draw the status bar "content"
		contentWidth = int(round(state * float(size[0])))
		for x in range(contentWidth):
			for y in range(size[1] - 1):
				self.drawPixel((pos[0] + x, pos[1] + y), colour)
