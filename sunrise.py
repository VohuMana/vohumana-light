import math
import datetime

class SunTimes:
	def __init__(self):
		self.sunrise = datetime.time()
		self.sunset = datetime.time()

# Constants
twoPi = math.pi * 2.0
sunRadius = 0.53
atmosphericRefraction = 34.0 / 60.0
DEG_TO_RAD = math.pi / 180.0
RAD_TO_DEG = 180.0 / math.pi

# Convert a month, day, year, and hour to the Julian representation
def ConvertToJulian(day, month, year, hour):
	julian = -7 * (year + (month + 9) / 12) / 4 + 275 * month / 9 + day;
	julian = julian + int(year * 367)
	julian = julian - 730531.5 + hour / 24.0
	return julian

# Force a number into the range of 0 and PI
def ForcePIRange(x):
	b = x / twoPi
	a = twoPi * (b - int(b))
	if( a < 0):
		a = a + twoPi
	return a

# Calculate the hour angle at a latitude
def CalculateHourAngle(lat, declination):
	dfo = DEG_TO_RAD * (0.5 * sunRadius + atmosphericRefraction)
	if(lat < 0.0):
		dfo = -dfo
	fo = math.tan(declination + dfo) * math.tan(lat * DEG_TO_RAD)

	if(fo > 0.999999):
		fo = 1.0

	fo = math.asin(fo) + math.pi / 2.0
	return fo

# Calculate the hour angle for twilight at a latitude
def CalculateTwilightHourAngle(lat, declination):
	dfo = DEG_TO_RAD * 6.0
	if(lat < 0.0):
		dfo = -dfo
	fo = math.tan(declination + dfo) * math.tan(lat * DEG_TO_RAD)
	fo = math.asin(fo) + math.pi / 2.0
	return fo

# Calculate values specific to the sunrise/sunset program
def CalculateL(juilianDate):
	return ForcePIRange(280.461 * DEG_TO_RAD + .9856474 * DEG_TO_RAD * juilianDate)

def CalculateG(juilianDate):
	return ForcePIRange(357.528 * DEG_TO_RAD + .9856003 * DEG_TO_RAD * juilianDate)

def EclipticLongitude(L, G):
	return ForcePIRange(L + 1.915 * DEG_TO_RAD * math.sin(G) + 0.02 * DEG_TO_RAD * math.sin(2.0 * G))

# Calculate the sunrise and sunset for a specific time zone
def CalculateSunriseAndSet(lat, lon, timezone, day, month, year, hour, isDST):
	julian = ConvertToJulian(day, month, year, hour)
	L = CalculateL(julian)
	G = CalculateG(julian)
	lmda = EclipticLongitude(L, G)
	oblique = 23.439 * DEG_TO_RAD - 0.0000004 * DEG_TO_RAD * julian
	alpha = math.atan2(math.cos(oblique) * math.sin(lmda), math.cos(lmda))
	delta = math.asin(math.sin(oblique) * math.sin(lmda))
	LL = L - alpha

	if(L < math.pi):
		LL = LL + twoPi

	equation = 1440.0 * (1.0 - LL / twoPi)

	hourAngle = CalculateHourAngle(lat, delta)
	twilightHourAngle = CalculateTwilightHourAngle(lat, delta)

	twilightLen = 12.0 * (hourAngle - twilightHourAngle) / math.pi
	dayLength = RAD_TO_DEG * hourAngle / 7.5
	if(dayLength < 0.00001):
		dayLength = 0.0

	rise = 12.0 - 12.0 * hourAngle / math.pi + timezone - lon / 15.0 + equation / 60.0
	set = 12.0 + 12.0 * hourAngle / math.pi + timezone - lon / 15.0 + equation / 60.0

	sunRiseHour = int(rise)
	sunRiseMinute = int((rise - sunRiseHour) * 60.0)

	sunSetHour = int(set)
	sunSetMinute = int((set - sunSetHour) * 60.0)

	if(True == isDST):
		sunRiseHour = sunRiseHour + 1
		sunSetHour = sunSetHour + 1

	times = SunTimes()
	times.sunrise = datetime.time(sunRiseHour, sunRiseMinute)
	
	times.sunset = datetime.time(sunSetHour, sunSetMinute)

	return times

# Testing
# Seattle Lat: 47.6097 Lon: -122.3331
# Expected output for 21/10/14
# My outputs: 7:36 and 18:11 
# Sunrise: 7:37
# Sunset: 18:10
# print("Finding Sunrise and sunet for Seattle for Oct 21st 2014")
# t = CalculateSunriseAndSet(47.6097, -122.3331, -8, datetime.datetime.now().date().day, datetime.datetime.now().date().month, datetime.datetime.now().date().year, datetime.datetime.now().time().hour, False)
# print("Sunrise: " + t.sunrise.isoformat() + " Sunset: "  + t.sunset.isoformat())
# More testing

#print(datetime.datetime.now().time().isoformat())

# Fort Collins: Lat: 40.5592 N Lon: 105.0781 
# print("\nFinding Sunrise and sunet for Fort Collins for Oct 21st 2014")
# print(CalculateSunriseAndSet(40.5592, -105.0781, -7, 21, 10, 2014, 0, True))

# print(CalculateSunriseAndSet(25.249, 55.299, 4, 21, 10, 2015, 0, True))

# How not brown cow , Hello world Hello my name is Katie and I should be reading my mathbook but I don't feel like it and we're going to talk about it tomorrow in class anyway so it doesn't really matter that much, right? right. yes. go away.