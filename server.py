from flask import Flask, request
from StringIO import StringIO

from PIL import Image
import epd7in5b

app = Flask(__name__)


@app.route('/epd', methods=('POST',))
def update_image():
    image = Image.open(StringIO(request.data))
    epd = epd7in5b.EPD()
    epd.init()
    epd.display_frame(epd.get_frame_buffer(image))
    return "ok"

app.run(host='0.0.0.0', debug=True)
