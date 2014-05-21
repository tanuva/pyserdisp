import ctypes
from ctypes import c_int, c_long, c_ubyte

class Serdisp:
	def __init__(self, device, model, options = ""):
		self.device = device
		self.model = model
		self.options = options

	def __enter__(self):
		class SerdispInternal:
			def __init__(self, device, model, options):
				self.turnOffOnQuit = True
				self.sdl = ctypes.CDLL("libserdisp.so")
				self.conn = self.sdl.SDCONN_open(device)

				if self.conn == 0:
					raise Exception("Couldn't open display device!")
				
				self.disp = self.sdl.serdisp_init(self.conn, model, options)
				self.clear() # display might be full of randomness if we don't clear here

			# constructs a single 32bit integer from a tuple (a, r, g, b)
			def __pack(self, rgbTuple):
				if not len(rgbTuple) in [3, 4]:
					raise Exception("Colour tuples should be (A)RGB formatted.")

				argb = ()

				if len(rgbTuple) == 4:
					argb = (rgbTuple[0] << 8) + rgbTuple[1]
					argb = (argb << 8) + rgbTuple[2]
					argb = (argb << 8) + rgbTuple[3]
				elif len(rgbTuple) == 3:
					# Assuming alpha as fully opaque
					argb = (0xFF << 8) + rgbTuple[0]
					argb = (argb << 8) + rgbTuple[1]
					argb = (argb << 8) + rgbTuple[2]
				
				return c_long(argb)

			# extracts separate argb values from a 32bit integer
			def __unpack(self, argb):
				rgbTuple = ()
				rgbTuple[0] = (argb & 0xff000000) >> 24
				rgbTuple[1] = (argb & 0x00ff0000) >> 16
				rgbTuple[2] = (argb & 0x0000ff00) >> 8
				rgbTuple[3] =  argb & 0x000000ff

			def setTurnOffOnQuit(self, turnOffOnQuit):
				self.turnOffOnQuit = turnOffOnQuit

			# serdisp_control.h
			# =================

			# TODO move SDCONN_open and serdisp_init here (as one)

			def close(self):
				self.sdl.serdisp_close(self.disp)

			def quit(self):
				self.sdl.serdisp_quit(self.disp)

			def reset(self):
				self.sdl.serdisp_reset(self.disp)

			def fullReset(self):
				self.sdl.serdisp_fullreset(self.disp)

			def setPixel(self, pos, colour):
				self.sdl.serdisp_setpixel(self.disp, c_int(pos[0]), c_int(pos[1]), c_int(colour))

			def getPixel(self, pos):
				return self.sdl.serdisp_setpixel(self.disp, c_int(pos[0]), c_int(pos[1]))

			def clear(self):
				self.sdl.serdisp_clear(self.disp)

			def clearBuffer(self):
				self.sdl.serdisp_clearbuffer(self.disp)

			def update(self):
				self.sdl.serdisp_update(self.disp)

			def rewrite(self):
				self.sdl.serdisp_rewrite(self.disp)

			def blink(self, what, count, delta):
				if count < 0:
					raise Exception("\"count\" should rather be positive")
				if delta < 0:
					raise Exception("\"delta\" should rather be positive")

				if what == "backlight":
					what = 0
				elif what == "pixels":
					what = 1

				self.sdl.serdisp_blink(self.disp, what, c_int(count), c_int(delta))

			def getWidth(self):
				return self.sdl.serdisp_getwidth(self.disp)

			def getHeight(self):
				return self.sdl.serdisp_getheight(self.disp)

			def getColours(self):
				return self.sdl.serdisp_getcolours(self.disp)

			def getDepth(self):
				return self.sdl.serdisp_getdepth(self.disp)

			def getPixelAspect(self):
				return self.sdl.serdisp_getpixelaspect(self.disp)

			def getDisplayName(self):
				return self.model # serdisplib does the same anyway

			def isDisplay(self):
				return bool(self.sdl.serdisp_isdisplay(self.display))

			# TODO display description functions
			# TODO display options

			# serdisp_colour.h
			# ================

			# Format: ARGB
			BLACK	= (255, 0, 0, 0)
			WHITE	= (255, 255, 255, 255)
			RED		= (255, 255, 0, 0)
			GREEN	= (255, 0, 255, 0)
			BLUE	= (255, 0, 0, 255)

			def getColour(self, pos):
				col = self.sdl.serdisp_getcolour(self.disp, c_int(pos[0]), c_int(pos[1]))
				return self.__unpack(col)

			def getGrey(self, pos):
				return self.sdl.serdisp_getgrey(self.disp, c_int(pos[0]), c_int(pos[1]))

			def setColour(self, pos, color):
				self.sdl.serdisp_setcolour(self.disp, c_int(pos[0]), c_int(pos[1]), self.__pack(color))

			def setGrey(self, pos, grey):
				if grey < 0 or grey > 255:
					raise Exception("Grey value must be within [0, 255]")

				self.sdl.serdisp_setgrey(self.disp, c_int(pos[0]), c_int(pos[1]), c_ubyte(grey))

			def transColour(self, argbColour):
				return self.sdl.serdisp_transcolour(self.disp, c_long(argbColour))

			def transGrey(self, grey):
				return self.sdl.serdisp_transgrey(self.disp, c_ubyte(grey))

			def lookupColour(self, argbColour):
				return self.sdl.serdisp_lookupcolor(self.disp, c_long(argbColour))

			def lookupGrey(self, grey):
				return self.sdl.serdisp_lookupgrey(self.disp, c_long(grey))

			# serdisp_messages.h
			# ==================

			def runtimeError(self):
				return self.sdl.sd_runtime_error() == 1

			def getErrorMsg(self):
				return self.sdl.sd_geterrormsg()

			def getDebugLevel(self):
				lvl = self.sdl.sd_getdebuglevel()

				if lvl == 0:
					return "warn"
				elif lvl == 1:
					return "info"
				elif lvl == 2:
					return "verbose"

			def setDebugLevel(self, lvl):
				if lvl == "warn":
					self.sdl.sd_setdebuglevel(0)
				elif lvl == "info":
					self.sdl.sd_setdebuglevel(1)
				elif lvl == "verbose":
					self.sdl.sd_setdebuglevel(2)
				else:
					raise Exception("Invalid debug level: " + lvl)

			def setLogMedium(self, medium):
				# FIXME
				print "Serdisp.setLogMedium: log medium docs are incomplete, this might fail."

				if medium == "syslog":
					self.sdl.sd_setlogmedium(0)
				elif medium == "stderr":
					self.sdl.sd_setlogmedium(1)
				elif medium == "stdout":
					self.sdl.sd_setlogmedium(2)
				else:
					raise Exception("Invalid log medium: " + medium)

		self.serdispInternal = SerdispInternal(self.device, self.model, self.options)
		return self.serdispInternal

	def __exit__(self, type, value, traceback):
		if self.serdispInternal.turnOffOnQuit:
			self.serdispInternal.clear()
			self.serdispInternal.quit()
		else:
			self.serdispInternal.close()
