pyserdisp
=========

Thin Python bindings for serdisplib >= 1.96.
I've tried to make parameters more pythonic where applicable. Still, most calls fit with the original [http://serdisplib.sourceforge.net/ serdisplib docs].

The "raw" bindings are available in `pyserdisp.py`, `graphdisp.py` contains high-level drawing functions for images and text.

Usage
=====

Pass device descriptor and display model the way serdisp_init expects them.
You may use `Serdisp.setTurnOffOnQuit(bool)` to prevent the display from being turned off when leaving the with statement.

````
from pyserdisp import Serdisp

with Serdisp("USB:7c0/1501", "CTINCLUD") as serdisp:
	serdisp.setColour([0, 0], serdisp.BLACK)
````
