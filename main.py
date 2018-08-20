# -*- coding: utf-8 -*-
import visualization

image = visualization.generate()
image.show()
io = StringIO()
image.save(io, format='PNG')
image_data = io.getvalue()
# requests.post('http://192.168.0.157:5000/epd', data=image_data)
