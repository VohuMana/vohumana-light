from flask import Flask
from bootstrap import *
from AnimThreading import *
from flask.ext.restful import reqparse
from sunrise import *
import datetime

# Parsers for obtaining data
fillParser = reqparse.RequestParser()
fillParser.add_argument('r', type = int, required = True, location = 'args')
fillParser.add_argument('g', type = int, required = True, location = 'args')
fillParser.add_argument('b', type = int, required = True, location = 'args')

breathingParser = reqparse.RequestParser()
breathingParser.add_argument('r', type = int, required = True, location = 'args')
breathingParser.add_argument('g', type = int, required = True, location = 'args')
breathingParser.add_argument('b', type = int, required = True, location = 'args')
breathingParser.add_argument('min', type = float, required = True, location = 'args')
breathingParser.add_argument('max', type = float, required = True, location = 'args')

alarmParser = reqparse.RequestParser()
alarmParser.add_argument('hour', type = int, required = True, location = 'args')
alarmParser.add_argument('min', type = int, required = True, location = 'args')

# Spawns flask on it's own thread
class ThreadedFlask(object):
	def __init__(self, f):
		self.app = f

	def StartOnThread(self):
		self.app.run(host='0.0.0.0', port=80, debug=False)

	def Go(self):
		threading.Thread(target=self.StartOnThread).start()

app = Flask(__name__)
tf = ThreadedFlask(app)

"""
http://<IP>/interpolate
"""
@app.route("/interpolate")
def RandomInterpolate():
	anim = InterpolateRandomColors(led, Color(255,0,0), Color(0,0,0))
	GTC.KickOffAnimation(anim)
	return "Hello Anim!"

"""
Expected URL request:
http://<IP>/fill?r=<red>&g=<green>&b=<blue>
"""
@app.route("/fill")
def fillLEDS():
	args = fillParser.parse_args()
	GTC.ChangeToNop()
	led.fill(Color(args['r'], args['g'], args['b']))
	led.update()
	return "Fill"

"""
Expected URL request:
http://<IP>/breathing?r=<red>&g=<green>&b=<blue>&min=<min brightness>&max=<max brightness>
"""
@app.route("/breathing")
def simpleBreathing():
	args = breathingParser.parse_args()
	anim = BreathingLight(led, Color(args['r'], args['g'], args['b']), args['min'], args['max'])
	GTC.KickOffAnimation(anim)
	return "BreathingLight"

"""
http://<IP>/sexy
"""
@app.route("/sexy")
def sexyTime():
	anim = SexyLight(led, 0.3, 1.0)
	GTC.KickOffAnimation(anim)
	return "Sexy Time ;)"

"""
http://<IP>/time
"""
@app.route("/time")
def whatTime():
	anim = TimeAnim(led)
	GTC.KickOffAnimation(anim)
	return "Time:" + datetime.datetime.now().time().isoformat()

# Used to find which light this is, only applicable in case of multiple lights
@app.route("/reportName")
def ReportName():
	return "VohuManaBedroom"

# Should never need this but just in case
@app.route("/kill")
def kill():
	GTC.KillThread()
	return "DEAD!"

@app.route("/off")
def turnOff():
	GTC.ChangeToNop()
	led.fill(Color(0,0,0))
	led.update()
	return "Light off"

# Add Sunrise time running on own thread to notify about time
@app.route("/sunrise")
def enableSunrise():
	times = CalculateSunriseAndSet(47.6097, -122.3331, -8, datetime.datetime.now().date().day, datetime.datetime.now().date().month, datetime.datetime.now().date().year, datetime.datetime.now().time().hour, False)
	anim = SunriseAnim(led, times)
	GTC.KickOffAnimation(anim)
	return times.sunrise.isoformat()

# Use the same sunrise code as an alarm
@app.route("/alarm")
def enableAlarm():
	args = alarmParser.parse_args()
	times = SunTimes()
	times.sunrise = datetime.time(args['hour'], args['min'])
	times.sunset = datetime.datetime.now().time()
	anim = SunriseAnim(led, times)
	return "Alarm set for " + times.sunrise.isoformat()

# Starts the web server
if __name__ == "__main__":
    tf.Go()
    GTC.InitThread()

# Add RainbowCycle
# Add chasing light

"""
Current Routes:
http://<IP>/interpolate
http://<IP>/fill?r=<red>&g=<green>&b=<blue>
http://<IP>/breathing?r=<red>&g=<green>&b=<blue>&min=<min brightness>&max=<max brightness>
http://<IP>/sexy
http://<IP>/kill
http://<IP>/reportName
http://<IP>/time
http://<IP>/off
"""
