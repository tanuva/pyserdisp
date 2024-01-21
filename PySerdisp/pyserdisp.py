# coding: utf-8

# TODO
# - Try to fetch an error message from serdisplib upon failure to init the disp

import ctypes
from ctypes import *
from ctypes.wintypes import POINT #c_int, c_long, c_ubyte, c_wchar_p

class Serdisp:
	def __init__(self, device, model, options = b""):
		#print ("Device %r, Model %r" % (device.decode("utf-8"), model.decode("utf-8")))
		self.device = device
		self.model = model
		self.options = options
		self.turnOffOnQuit = True
		self.sdl = ctypes.CDLL("libserdisp.so")
		#self.setDebugLevel("verbose")
		self.init()
		self.clear() # display might be full of randomness if we don't clear here

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		if self.turnOffOnQuit:
			self.quit()
		else:
			self.close()

	# constructs a single 32bit integer from a tuple (a, r, g, b)
	def __pack(self, rgbTuple):
		argb = ()

		try:
			if len(rgbTuple) == 4:
				argb = (rgbTuple[0] << 8) + rgbTuple[1]
				argb = (argb << 8) + rgbTuple[2]
				argb = (argb << 8) + rgbTuple[3]
			elif len(rgbTuple) == 3:
				# Assuming alpha as fully opaque
				argb = (0xFF << 8) + rgbTuple[0]
				argb = (argb << 8) + rgbTuple[1]
				argb = (argb << 8) + rgbTuple[2]
		except Exception:
			raise Exception("Colour tuples should be [ARGB], [RGB] formatted. Is:", rgbTuple)

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

	OPTION_NO = 0
	OPTION_YES = 1
	OPTION_TOGGLE = 2

	# TODO move SDCONN_open and serdisp_init here (as one)
	def init(self):
		if self.sdl == 0:
			raise Exception("Couldn't initialise driver!")
		self.sdl.SDCONN_open.restype = POINTER(serdisp_CONN_t)
		self.conn = self.sdl.SDCONN_open(self.device)

		if self.conn == 0:
			raise Exception("Couldn't open display. Device: \"%s\" Model: \"%s\" \nError: %r" % (self.device.decode("utf-8"), self.model.decode("utf-8"), self.getErrorMsg().decode("utf-8")))
		self.sdl.serdisp_init.argtypes = (POINTER(serdisp_CONN_t), c_char_p, c_char_p,)
		self.sdl.serdisp_init.restype = POINTER(serdisp_t)
		self.disp = self.sdl.serdisp_init(self.conn, self.model, self.options)
		if self.disp == 0:
			raise Exception("Couldn't initialize the display!")

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
		return bool(self.sdl.serdisp_isdisplay(self.disp))

	def getOption(self, option):
		output = -1
		return self.sdl.serdisp_getoption(self.disp, option, output)

	def setOption(self, option, value):
		self.sdl.serdisp_setoption(self.disp, option, value)

	def isOption(self, option):
		return self.sdl.serdisp_isoption(self.disp, option)

	# TODO display description functions

	# serdisp_colour.h
	# ================

	# Format: ARGB
	BLACK	= (255, 0, 0, 0)
	WHITE	= (255, 255, 255, 255)
	RED	= (255, 255, 0, 0)
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
		return c_int.in_dll(self.sdl, "sd_runtimeerror").value == 0

	def getErrorMsg(self):
		errmsg = c_char * 255
		stri = errmsg.in_dll(self.sdl, "sd_errormsg")
		return stri.value

	def getDebugLevel(self):
		lvl = c_int.in_dll(self.sdl, "sd_debuglevel").value

		if lvl == 0:
			return "warn"
		elif lvl == 1:
			return "info"
		elif lvl == 2:
			return "verbose"

	def setDebugLevel(self, lvl):
		if lvl == "warn":
			c_int.in_dll(self.sdl, "sd_debuglevel").value = 0 #self.sdl.sd_setdebuglevel(0)
		elif lvl == "info":
			c_int.in_dll(self.sdl, "sd_debuglevel").value = 1 #self.sdl.sd_setdebuglevel(1)
		elif lvl == "verbose":
			c_int.in_dll(self.sdl, "sd_debuglevel").value = 2 #self.sdl.sd_setdebuglevel(2)
		else:
			raise Exception("Invalid debug level: " + lvl)

	def setLogMedium(self, medium):
		# FIXME
		print("Serdisp.setLogMedium: log medium docs are incomplete, this might fail.")

		if medium == "syslog":
			c_int.in_dll(self.sdl, "sd_logmedium").value #self.sdl.sd_setlogmedium(0)
		elif medium == "stderr":
			self.sdl.sd_setlogmedium(1)
		elif medium == "stdout":
			self.sdl.sd_setlogmedium(2)
		else:
			raise Exception("Invalid log medium: " + medium)
class spi(Structure):
		_fields_ = [("framelen", c_byte),
			  		("cpol", c_byte),
					("cpha", c_byte),
					("data_high", c_byte),
					("dc_extsig", c_byte),
					("prescaler", c_byte),
					("divider", c_uint16)]
class rs232(Structure):
		_fields_ = [("baudrate", c_uint),
			  		("c_cs8_decr", c_byte),
					("c_cstopb", c_byte),
					("c_parenb", c_byte),
					("c_parodd", c_byte),
					("c_cread", c_byte),
					("c_local", c_byte),
					("c_rtscts", c_byte),
					("c_set_vmin", c_byte),
					("c_set_vtime", c_byte),
					("c_cc_vmin", c_byte),
					("c_cc_vtime", c_byte)]
class serdisp_CONN_spi_t(Union):
		_fields_ = [("spi", spi),
			  		("rs232", rs232)]

class termios(Structure):
		_fields_ = [("c_iflag", c_uint),
			  		("c_oflag", c_uint),
					("c_cflag", c_uint),
					("c_lflag", c_uint),
					("c_line", c_ubyte),
					("c_cc", c_ubyte*32),
					("c_ispeed", c_uint),
					("c_ospeed", c_uint),]

class flags_t(Structure):
		_fields_ = [("needs_confinit", c_byte),
			  		("endian", c_byte),
					("directIO", c_byte),]

class serdisp_CONN_t(Structure):
		_fields_ = [("conntype", c_uint16),
			  		("hardwaretype", c_uint16),
					("protocol", c_uint16),
					("signals", c_uint32 * 16),
					("signals_permon", c_uint32),
					("signals_invert", c_uint32),
					("io_flags_readstatus", c_byte),
					("io_flags_writedata", c_byte),
					("io_flags_writecmd", c_byte),
					("io_flags_default", c_byte),
					("pp_ctrlbits_saved", c_byte),
					("port", c_uint16),
					("fd", c_int),
					("termstate_bkp", termios),
					("termstate", termios),
					("sdcdev", c_char_p),
					("debug_count", c_uint32),
					("extra", c_void_p),
					("timestamp", c_uint32),
					("flags", flags_t),
					("spi", serdisp_CONN_spi_t),
			  ]

class serdisp_options_t(Structure):
		_fields_ = [("name", c_char_p),
			  		("aliasnames", c_char_p),
					("minval", c_long),
					("maxval", c_long),
					("modulo", c_long),
					("flag", c_byte),
					("defines", c_char_p),]
		
class serdisp_wiresignal_t(Structure):
		_fields_ = [("conntype", c_uint16),
			  		("signalname", c_char_p),
					("activelow", c_int),
					("cord", c_char),
					("index", c_int),]

class serdisp_wiredef_t(Structure):
		_fields_ = [("id", c_int),
			  		("conntype", c_uint16),
					("name", c_char_p),
					("definition", c_char_p),
					("description", c_char_p),]

class serdisp_s(Structure):
		_fields_ = []

class serdisp_t(Structure):
		DISPFUNC_1 = CFUNCTYPE(POINTER(serdisp_s))
		DISPFUNC_2 = CFUNCTYPE(POINTER(serdisp_s), c_char_p, c_long)
		DISPFUNC_3 = CFUNCTYPE(POINTER(serdisp_s), c_char_p, POINTER(c_int))
		DISPFUNC_4 = CFUNCTYPE(POINTER(serdisp_s), c_int, c_int, c_uint32)
		DISPFUNC_5 = CFUNCTYPE(POINTER(serdisp_s), c_int, c_int)
		DISPFUNC_6 = CFUNCTYPE(POINTER(serdisp_s), c_uint32)
		DISPFUNC_7 = CFUNCTYPE(POINTER(serdisp_s), c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_char_p)
		DISPFUNC_8 = CFUNCTYPE(POINTER(serdisp_s), c_byte)
		_fields_ = [("dsp_name", c_char_p),
			  		("dsp_optionstring", c_char_p),
			  		("dsp_id", c_int),
			  		("width", c_int),
			  		("height", c_int),
			  		("depth", c_int),
			  		("startxcol", c_int),
			  		("startycol", c_int),
			  		("xreloctab", POINTER(c_int)),
			  		("yreloctab", POINTER(c_int)),
			  		("xcolgaps", c_int),
			  		("ycolgaps", c_int),
			  		("dsparea_width", c_long),
			  		("dsparea_height", c_long),
			  		("feature_contrast", c_bool),
			  		("feature_backlight", c_bool),
			  		("feature_invert", c_bool),
			  		("min_contrast", c_int),
			  		("max_contrast", c_int),
			  		("mid_contrast", c_int),
			  		("delay", c_long),
			  		("optalgo_maxdelta", c_int),
			  		("specific_data", c_void_p),
			  		("ctable", POINTER(c_uint32)),
			  		("colour_spaces", c_long),
			  		("default_bgcolour", c_uint32),
			  		("sdcd", POINTER(serdisp_CONN_t)),
			  		("connection_types", c_int),
			  		("curr_rotate", c_int),
			  		("curr_contrast", c_int),
			  		("curr_backlight", c_int),
			  		("curr_invert", c_int),
			  		("curr_dimming", c_int),
			  		("supp_protocols", c_int),
			  		("dbg_cnt", c_int),
					  
			  		("fp_init", DISPFUNC_1),
			  		("fp_update", DISPFUNC_1),
			  		("fp_clear", DISPFUNC_1),
			  		("fp_setoption", DISPFUNC_2),
			  		("fp_getoption", DISPFUNC_3),
			  		("fp_close", DISPFUNC_1),
			  		("fp_setsdpixel", DISPFUNC_4),
			  		("fp_getsdpixel", DISPFUNC_5),
			  		("fp_transsdcol", DISPFUNC_6),
			  		("fp_transsdgrey", DISPFUNC_8),
			  		("fp_lookupsdcol", DISPFUNC_6),
			  		("fp_lookupsdgrey", DISPFUNC_6),
			  		("fp_cliparea", DISPFUNC_7),
			  		("fp_getvalueptr", DISPFUNC_3),
			  		("fp_freeresources", DISPFUNC_1),
					  
			  		("scrbuf", c_char_p),
			  		("scrbuf_chg", c_char_p),
			  		("scrbuf_size", c_int),
			  		("scrbuf_chg_size", c_int),
			  		("scrbuf_bits_used", c_byte),
			  		("bbox_dirty", c_byte),
			  		("bbox", c_int*4),
			  		("wiresignals", POINTER(serdisp_wiresignal_t)),
			  		("wiredefs", POINTER(serdisp_wiredef_t)),
			  		("amountwiresignals", c_int),
			  		("amountwiredefs", c_int),
			  		("options", POINTER(serdisp_options_t)),
			  		("amountoptions", c_int),
			  		("remote_devid", c_byte),
			  		("gpevset", POINTER(c_void_p))]