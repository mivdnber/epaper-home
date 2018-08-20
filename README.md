# Home e-paper display

Turn a [Waveshare 7.5inch e-Paper HAT (B)](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B))
and an internet connected Raspberry Pi into a simple home dashboard.

## Setup

Sorry, Python 2 right now, because the Waveshare code is Python 2 only.

### On PC / Mac
```
virtualenv env
env/bin/pip install -r requirements.txt
```

Next, create a `config.py` file containing values for at least the following
configuration fields:

- `DARKSKY_API_FIELD`: a key for the [Dark Sky Weather API](https://darksky.net/).
  Alternatively, remove the weather widget in `visualization.py`
- `CALENDAR_ICS_URL`: a URL to an iCal file for the calendar widget.

Additionally, the code currently assumes you're using the Tahoma font stored in
`non-free-fonts/Tahoma.ttf`. You can copy Tahoma to that location (license
issues forbid me to bundle it), or you can configure a different font with the
`MAIN_FONT_FILE` configuration key.

Running `env/bin/python visualization.py` will show a preview of what should
soon be shown on your fancy e-ink display.

### The real deal

Follow [these instructions](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B)#How_to_use)
to get your Raspberry Pi in shape.

Copy the code to your Pi, follow the same setup procedure as above and try and run
`env/bin/python update.py` as a superuser. The display should update!

Next, set up a cron job to run the command (mine is set to update every 10 minutes), and you're done!
