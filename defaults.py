import os

MAIN_FONT_FILE = 'non-free-fonts/Tahoma.ttf'
ICON_FONT_FILE = 'fonts/fa-regular-400.ttf'
WEATHER_FONT_FILE = 'fonts/weathericons-regular.ttf'

DARKSKY_API_KEY = None
CALENDAR_ICS_URL = None

BUS_STOPS = [
    # Stop name, stop id, list of bus lines in which you're interested
    ('Ringvaartstraat', 202901, [44]),
    ('Nachtegaaldreef', 202905, [42])
]

try:
    from config import *
except ImportError:
    print 'Please create config.py!'
    raise

if DARKSKY_API_KEY is None:
    raise RuntimeError('Please fill in DARKSKY_API_KEY in config.py')

if CALENDAR_ICS_URL is None:
    raise RuntimeError('Please fill in CALENDAR_ICS_URL in config.py')

if not os.path.exists(MAIN_FONT_FILE):
    raise RuntimeError('MAIN_FONT_FILE points to a non-existent file!')

if not os.path.exists(ICON_FONT_FILE):
    raise RuntimeError('ICON_FONT_FILE points to a non-existent file!')

if not os.path.exists(WEATHER_FONT_FILE):
    raise RuntimeError('WEATHER_FONT_FILE points to a non-existent file!')
