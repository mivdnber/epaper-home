# -*- coding: utf-8 -*-
import epd7in5b
import visualization

image = visualization.generate()
epd = epd7in5b.EPD()
epd.init()
epd.display_frame(epd.get_frame_buffer(image))
