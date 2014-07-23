# Widgets

The widgets module contains some high-level widgets that build upon the PySerdisp API.

## Text
<hr />
This widget uses `freetype-py` to render text into a bitmap and draws that one.

The `halign` and `valign` keyword arguments can be used to specify horizontal and/or vertical alignment. If alignment is set to right (instead of the default "left"), the position argument will be interpreted as an offset from the top right corner instead of the top left one. The same goes for vertical alignment and the bottom right corner.

### Constructor
- `serdisp` The PySerdisp instance to draw the pixels with
- `position` Text position as a 2-tuple or list, ex.: (20,4)
- `fontpath` Absolute or relative path to a TrueType font file
- `fontsize` Font size in points (as usual)
- `text` The actual text to display
- kwargs:
	- `halign` Can be one of: center, right
	- `valign` Can be one of: center, bottom

### Members
- `draw()`
- `setText(str)`


## Pixmap
<hr />
Draws a pixmap from a file. Pixels are drawn 1:1 - if the image is larger than the display, excess pixels are ignored.

### Constructor
- `serdisp` The PySerdisp instance to draw the pixels with
- `path` Absolute or relative path to the image file
- `position` Upper left corner as a 2-tuple or list, ex.: (20,4)

### Members
- `draw()`
- `erase()` Erases the area occupied by the image with white

## Progress Bar
<hr />
Draws a simple progress bar that can have a border.

### Constructor
- `serdisp` The PySerdisp instance to draw the pixels with
- `position` Upper left corner as a 2-tuple or list, ex.: (20,4)
- `size` Progress bar size as a 2-tuple or list
- kwargs
	- `state` The initial progress state. float, 0.0 <= state <= 1.0
	- `border` Turns border drawing on or off. Only possible if the bar is at least 3 pixels high and wide. boolean.

### Members
- `draw()`
- `setState(float)`