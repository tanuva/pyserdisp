# Hey there!

I've tried and kept the python bindings as close to the original Serdisplib API as possible while using pythonic types. Therefore, I won't provide documentation for each and every Serdisplib function, better refer to the [original docs](http://serdisplib.sourceforge.net/).

The fancier part is the `widget` module which contains some widget classes I put together. These have their [own documentation](widget.md).

## Usage
This looks quite reasonable to me, I hope it does to you, too:

```
from pyserdisp import Serdisp
from time import sleep

on = True

with Serdisp("USB:7c0/1501", "CTINCLUD") as serdisp:
	while True:
		if on:
			serdisp.setColour([0, 0], serdisp.BLACK)
		else:
			serdisp.setColour([0, 0], serdisp.WHITE)
		on = not on
		sleep(1)
```

The with statement ensures that the display device is closed properly even if the program crashes.

The Serdisp constructor parameters are directly passed on to Serdisplib where the first is the display device and the second is the display model. For the device, refer to the [SDCONN_open](http://serdisplib.sourceforge.net/docs/index.html#serdisp_connect__SDCONN_open) docs. The display model can be found by looking your display controller up in the [list of supported displays](http://serdisplib.sourceforge.net/#displays) and taking the exact value stated in the "name in serdisplib" field on the description page.

To keep the display turned on after you closed the device, you need to set `Serdisp.setTurnOffOnQuit(False)`.
