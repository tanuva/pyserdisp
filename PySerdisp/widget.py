# coding=utf-8

from math import ceil
from pyserdisp import Serdisp
from textrenderer import Font
import time
from PIL import Image
import os
import sys
class Pixmap:
	def __init__(self, serdisp, path, position):
		if not isinstance(serdisp, Serdisp):
			raise ValueError("serdisp must be a Serdisp instance!")

		self.serdisp = serdisp
		self.path = path
		self.position = position
		if position[0] < 0 or position[1] < 0:
			print("Warning: position of", path, "is < 0:", position)

		# load the image
		img = None
		try:
			img = Image.open(path)
			img.load()
		except IOError as e:
			print("Warning: Couldn't open", path)
			print(e)
			return

		# TODO only if necessary
		img.convert("1") # Convert to black/white mode
		imgData = list(img.getdata())
		self.size = img.size
		self.data = [imgData[i * self.size[0]:(i + 1) * self.size[0]] for i in range(self.size[1])]

	def draw(self):
		"""
		Draws the pixmap at the given location.
		"""
		for x in range(self.size[0]):
			for y in range(self.size[1]):
				# HACK: Just taking the red value here since we
				# hardcoded conversion to greyscale above.
				#print("y%i x%i b%i" % (x, y, self.data[y][x]))
				b = 0
				if (self.data[y][x][0] > 0): b = 255
				self.serdisp.setGrey((x+self.position[0], y+self.position[1]), b) #self.data[y][x][0]

	def erase(self):
		"""
		Sets every pixel of the affected region to white.
		"""
		for x in range(self.size[0]):
			for y in range(self.size[1]):
				self.serdisp.setGrey((x, y), (255, 255, 255, 255))

class Text:
	def __init__(self, serdisp, position, fontpath, fontsize, text, **kwargs):
		self.serdisp = serdisp
		# Store user defined pos/offsets separately, we must not overwrite those in setText!
		self.userPos = position
		# These values may be altered by setText (actual rendering position)
		self.position = list(position)

		if not os.path.isfile(fontpath):
			raise ValueError("Font doesn't exist:", fontpath)

		self.kwargs = kwargs
		self.font = Font(fontpath, fontsize)
		self.setText(text)
		self.lastSlice = 0
		self.lastDrawTime = None

		if "sliceDuration" in list(self.kwargs.keys()):
		    self.sliceDuration = float(self.kwargs["sliceDuration"])
		else:
		    self.sliceDuration = 5.0

	def setText(self, text):
		"""
		Alignment:
		halign can be one of ["left", "center", "right"]
		valign can be one of ["top", "center", "bottom"]
		If an alignment is specified, the corresponding textpos coordinate
		is interpreted as offset from that display edge or ignored for "center".
		"""

		self.text = text
		self.bitmap = self.font.render_text(self.text)
		self.size = [
			int(round(min(self.bitmap.width, self.serdisp.getWidth() - 2))),
			int(round(min(self.bitmap.height, self.serdisp.getHeight() - 2)))
		]

		# Compute text slice count to show sequentially if text is wider
		# than the display.
		if len(self.text) > 0:
		    self.sliceCount = int(ceil(self.bitmap.width / float(self.size[0])))
		else:
		    self.sliceCount = 1

		# Setup of the actual rendering position (might be different from self.userPos!)
		if "halign" in list(self.kwargs.keys()):
			if self.kwargs["halign"] == "center":
				self.position[0] = max(2, int((self.serdisp.getWidth() / 2.0) - (self.bitmap.width / 2.0)))
			elif self.kwargs["halign"] == "right":
				self.position[0] = self.serdisp.getWidth() - self.bitmap.width - self.userPos[0]
		if "valign" in list(self.kwargs.keys()):
			if self.kwargs["valign"] == "center":
				self.position[1] = max(2, int(round((self.serdisp.getHeight() / 2.0) - (self.bitmap.height / 2.0))))
			elif self.kwargs["valign"] == "bottom":
				self.position[1] = self.serdisp.getHeight() - self.bitmap.height - self.userPos[1]

	def __getCurrentSliceIdx(self):
		slcIdx = self.lastSlice

		if not self.lastDrawTime:
			self.lastDrawTime = time.time()
			slcIdx = 0
		elif (time.time() - self.lastDrawTime) > self.sliceDuration:
			self.lastDrawTime = time.time()
			slcIdx = (slcIdx + 1) % self.sliceCount

		assert(slcIdx < self.sliceCount)
		return slcIdx

	def __getSlice(self, slcIdx):
		slcWidth = self.size[0]
		txtWidth = self.bitmap.width

		divWidth = txtWidth / self.sliceCount
		slcCenter = slcIdx * divWidth + (divWidth / 2)

		if slcIdx == 0:
			return [0, slcWidth]
		elif slcIdx == self.sliceCount - 1:
			return [txtWidth - slcWidth, txtWidth]
		else:
			return [round(slcCenter - slcWidth / 2),
				round(slcCenter + slcWidth / 2)]

	def draw(self):
		slcIdx = self.__getCurrentSliceIdx()
		self.lastSlice = slcIdx
		#print("Drawing: \"%s\" (%i, %i of %i)" % (self.text, self.lastSlice + 1, self.sliceCount))
		slc = self.__getSlice(slcIdx)
		intWidth = round(self.bitmap.width)

		for y in range(self.size[1]):
			for x in range(slc[1] - slc[0]):
				pixpos = [self.position[0] + x, self.position[1] + y]
				pixel = (1 - self.bitmap.pixels[slc[0] + x + y * intWidth]) * 255
				self.serdisp.setGrey(pixpos, pixel)

class Progressbar:
	def __init__(self, serdisp, position, size, **kwargs):
		if not isinstance(serdisp, Serdisp):
			raise ValueError("serdisp must be an instance of Serdisp.")

		self.serdisp = serdisp

		if position[0] < 0 or position[1] < 0:
			raise ValueError("pos must not be negative")
		self.position = position

		if size[0] < 1 or size[1] < 1:
			raise ValueError("size must be greater than 1")
		self.size = size

		# Ugly! But that is the pythonic way, isn't it?
		try:
			self.setState(kwargs["state"])
		except:
			self.setState(0.0)
		try:
			self.drawBorder = kwargs["border"]
			if self.drawBorder and (size[0] < 3 or size[1] < 3):
				print("Warning: progress bar cannot have a border if x/y size is < 3:", size)
				self.drawBorder = False
		except:
			self.drawBorder = True
		try:
			self.colour = kwargs["colour"]
		except:
			self.colour = (255, 0, 0, 0)

	def setState(self, state):
		self.state = min(1, max(0, state))

	def draw(self):
		if self.drawBorder:
			for x in range(self.size[0]):
				self.serdisp.setColour((self.position[0] + x, self.position[1]), self.colour)
				self.serdisp.setColour((self.position[0] + x, self.position[1] + self.size[1] - 1), self.colour)
			for y in range(self.size[1] - 1):
				self.serdisp.setColour((self.position[0], self.position[1] + y), self.colour)
				self.serdisp.setColour((self.position[0] + self.size[0] - 1, self.position[1] + y), self.colour)

		# draw the status bar "content"
		contentWidth = int(round(self.state * float(self.size[0])))
		for x in range(contentWidth):
			for y in range(self.size[1] - 1):
				self.serdisp.setColour((self.position[0] + x, self.position[1] + y), self.colour)
