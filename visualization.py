# -*- coding: utf-8 -*-
import sys
import locale
import time
from datetime import datetime, date, timedelta
from StringIO import StringIO

from PIL import Image, ImageDraw, ImageFont
import requests
import forecastio
import vobject
import pytz

from defaults import *


try:
    locale.setlocale(locale.LC_TIME, 'nl_BE')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'nl_BE.utf8')

EPD_WIDTH = 640
EPD_HEIGHT = 384

BLACK = 0
RED = 127
WHITE = 255

TITLE_FONT = ImageFont.truetype(MAIN_FONT_FILE, 40)
MAIN_FONT = ImageFont.truetype(MAIN_FONT_FILE, 24)
SMALL_FONT = ImageFont.truetype(MAIN_FONT_FILE, 18)
ICON_FONT = ImageFont.truetype(ICON_FONT_FILE, 24)
SMALL_ICON_FONT = ImageFont.truetype(ICON_FONT_FILE, 18)
HUGE_ICON_FONT = ImageFont.truetype(ICON_FONT_FILE, 72)

class Widget(object):

    def draw(self):
        raise NotImplementedError

    def draw_on(self, image, coords):
        widget_image = self.draw()
        image.paste(widget_image, coords)

    def create_image(self, width, height):
        return Image.new('L', (width, height), WHITE)


class WeatherIcon(Widget):
    icons = {
        'clear-day': u'\uf00d',
        'clear-night': u'\uf02e',
        'rain': u'\uf019',
        'snow': u'\uf01b',
        'sleet': u'\uf0b5',
        'wind': u'\uf050',
        'fog': u'\uf014',
        'cloudy': u'\uf013',
        'partly-cloudy-day': u'\uf002',
        'partly-cloudy-night': u'\uf031',
        'hail': u'\uf015',
        'thunderstorm': u'\uf01e',
        'tornado': u'\uf056',
    }
    font = ImageFont.truetype(WEATHER_FONT_FILE, 30)

    def __init__(self, date, icon_name, temperature, width=50):
        self._date = date
        self._icon_name = icon_name
        self._icon = self.icons[icon_name]
        self._temperature = temperature
        self._width = width

    def draw(self):
        image = self.create_image(self._width, 90)
        draw = ImageDraw.Draw(image)
        draw.fontmode = '1'
        day = self._date.strftime('%a')
        day_width, _ = draw.textsize(day, font=MAIN_FONT)
        day_x = (self._width - day_width) / 2
        draw.text((day_x, 0), self._date.strftime('%a'), font=MAIN_FONT, fill=BLACK)
        icon_width, _ = draw.textsize(self._icon, font=self.font)
        icon_x = (self._width - icon_width) / 2
        draw.text((icon_x, 28), self._icon, font=self.font, fill=BLACK)
        # temp = u'{}°'.format(int(round(self._temperature)))
        temp = u'{}'.format(int(round(self._temperature)))
        temp_width, _ = draw.textsize(temp, font=MAIN_FONT)
        temp_x = (self._width - temp_width) / 2
        draw.text((temp_x, 64), temp, font=MAIN_FONT, fill=BLACK)
        return image


class WeatherForecast(Widget):
    key = DARKSKY_API_KEY
    lat, lng = 51.008651,3.754532
    huge_icon_font = font = ImageFont.truetype(WEATHER_FONT_FILE, 80)

    def __init__(self):
        forecast = forecastio.load_forecast(self.key, self.lat, self.lng, units="si")
        self._days = forecast.daily().data[1:]

    def draw(self):
        image = self.create_image(50 * len(self._days), 120)
        draw = ImageDraw.Draw(image)
        draw.fontmode = '1'
        icon_width, icon_height = draw.textsize(WeatherIcon.icons[self._days[0].icon], font=self.huge_icon_font)
        draw.text((0, 0), WeatherIcon.icons[self._days[0].icon], font=self.huge_icon_font, fill=BLACK)
        temp = u'{}'.format(int(round(self._days[0].temperatureHigh)))
        temp_width, temp_height = draw.textsize(temp, font=MAIN_FONT)
        draw.text(((icon_width - temp_width) / 2 - 15, (icon_height - temp_height) / 2 * 1.5), temp, font=MAIN_FONT, fill=BLACK)
        for i, day in enumerate(self._days[1:5]):
            icon = WeatherIcon(day.time, day.icon, day.temperatureHigh)
            icon.draw_on(image, (120 + i * 50, 0))
        return image


class Title(Widget):

    def __init__(self):
        
        self._date_string = time.strftime('%A %-d %B').title()
 
    def draw(self):
        image = self.create_image(EPD_WIDTH, 56)
        draw = ImageDraw.Draw(image)
        draw.fontmode = '1'
        draw.text((0, 0), self._date_string, font=TITLE_FONT, fill=BLACK)
        return image


class Calendar(Widget):
    url = CALENDAR_ICS_URL

    def __init__(self):
        content = requests.get(self.url).text
        v = vobject.readOne(content)
        now = datetime.utcnow().replace(tzinfo=pytz.utc)

        def to_dt(d):
            if isinstance(d, datetime):
                return d
            return datetime(d.year, d.month, d.day, tzinfo=pytz.utc)

        self._events = sorted([
            (to_dt(event.dtstart.value), event.summary.value)
            for event in v.vevent_list
            if now + timedelta(days=30) > to_dt(event.dtstart.value) >= now
        ], key=lambda (dt, _): dt)[:3]


    def draw(self):
        image = self.create_image(600, 120)
        draw = ImageDraw.Draw(image)
        draw.fontmode = '1'
        draw.text((0, 0), u'\uf073', font=ICON_FONT, fill=BLACK)
        y = 0
        x = 32
        _, line_height = draw.textsize("foghorn", font=SMALL_FONT)
        today = date.today()
        weekdays_formatted = [
            (today + timedelta(days=i)).strftime(u'%a')
            for i in range(7)
        ]
        max_weekday_width = max(
            draw.textsize(x + ' ', font=SMALL_FONT)[0]
            for x in weekdays_formatted
        )
        max_day_with = max(draw.textsize(str("{:02d}".format(i))) for i in range(32))

        for dt, summary in self._events:
            line = u'{} {}'.format(dt.strftime(u'%a'), summary)
            draw.text((x, y), dt.strftime(u'%a'), font=SMALL_FONT, fill=BLACK)
            draw.text((x + max_weekday_width, y), dt.strftime(u'%d'), font=SMALL_FONT, fill=BLACK)
            draw.text((x + max_weekday_width + max_weekday_width + 10, y), summary, font=SMALL_FONT, fill=BLACK)

            y += line_height
        return image


class Busses(Widget):

    api_url = 'https://www.delijn.be/rise-api-core/haltes/doorkomstenditmoment/{}/13'
    
    stops = BUS_STOPS

    def __init__(self):
        self._busses = self._fetch_busses()
    
    def _fetch_busses(self):
        data = {}
        for stop, stop_id, lines in self.stops:
            api_url = self.api_url.format(stop_id)
            response = requests.get(api_url).json()
            data[stop] = [
                (datetime.fromtimestamp(l['vertrekCalendar'] / 1000), l['lijnNummerPubliek'], l['bestemming'])
                for l in response["lijnen"]
            ]
        return data

    def draw(self):
        image = self.create_image(EPD_WIDTH, 90)
        draw = ImageDraw.Draw(image)
        draw.fontmode = '1'
        x = 0
        title_height = max(draw.textsize(s[0], SMALL_FONT)[1] for s in self.stops)
        for stop, _, _ in self.stops:
            y = 0
            draw.text((x, y), u'\uf207', font=ICON_FONT, fill=BLACK)
            draw.text((x + 32, y), stop, font=SMALL_FONT, fill=BLACK)
            y += title_height + 4
            if not self._busses[stop]:
                message = 'Helaas pindakaas,\nde laatste bus is vertrokken :('
                draw.text((x, y), message, font=SMALL_FONT, fill=BLACK)
            for dt, nr, dest in self._busses[stop][:3]:
                draw.text((x, y), dt.strftime('%H:%M'), font=SMALL_FONT, fill=BLACK)
                draw.text((x + 60, y), '[{}]'.format(nr), font=SMALL_FONT, fill=BLACK)
                draw.text((x + 100, y), dest, font=SMALL_FONT, fill=BLACK)
                y += 18
            x += 260
        return image


def generate():
    image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), WHITE)    # 255: clear the frame
    Title().draw_on(image, (60, 30))
    WeatherForecast().draw_on(image, (60, 85))
    Calendar().draw_on(image, (60, 190))
    Busses().draw_on(image, (60, EPD_HEIGHT - 110))
    return image


def generate_as_bytes():
    image = generate()
    io = StringIO()
    image.save(io, format='PNG')
    return io.getvalue()


if __name__ == '__main__':
    generate().show()
