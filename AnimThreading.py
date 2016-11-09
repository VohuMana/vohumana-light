import threading
import time
import random
import datetime
from raspledstrip.color import *

# This is for the initial thread as well as when the light has been set to something that does not require a thread
def DoNothing(killEvent):
	# Block till event is set
	killEvent.wait()

class BaseAnimationClass(object):
		def __init__(self, printStr):
				self.string = printStr

		def animate(self, event):
			while not event.isSet():
				print(self.string)

# The global thread controller manages the single animation thread
class GlobalThreadController(object):
	def __init__(self):
		self.signalEvent = threading.Event()
		self.animThread = threading.Thread(target=DoNothing, args=(self.signalEvent,))

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.signalEvent.set()

	def KickOffAnimation(self, animObject):
		# Signal event
		self.signalEvent.set()
		# Wait for thread to die
		while self.animThread.isAlive():
			pass
		# Clear the event
		self.signalEvent.clear()
		# Spawn new thread
		self.animThread = threading.Thread(target=animObject.animate, args=(self.signalEvent,))
		# Kick off new thread
		self.animThread.start()

	def ChangeToNop(self):
		self.signalEvent.set()
		while self.animThread.isAlive():
			pass
		self.signalEvent.clear()
		self.animThread = threading.Thread(target=DoNothing, args=(self.signalEvent,))
		self.animThread.start()

	def KillThread(self):
		self.signalEvent.set()

	def InitThread(self):
		self.animThread.start()

GTC = GlobalThreadController()

# Randomly fades between colors, 4s is good for smooth transistions
class InterpolateRandomColors(BaseAnimationClass):
	def __init__(self, leds, initColor, otherColor, time=4):
		self.color1 = initColor
		self.color2 = otherColor
		self.seconds = time
		self.led = leds

	def InterpolateOverTime(self, led,color1, color2, seconds, killEvent):
			tempColor = Color(0,0,0)
			elapsedTimeMs = 0
			maxTimeMs = seconds * 1000
			# While we are not done
			while elapsedTimeMs < maxTimeMs:
				# If a change has been requested break out
				if killEvent.isSet():
					break
				# Get the start time
				start_time = int(round(time.time() * 1000))
				# Update color values
				# Simple Linear Interpolate equation: y = (1 - t) * alpha + t * beta
				t = float(elapsedTimeMs) / float(maxTimeMs)
				tempColor.r = ((1.0 - t) * color1.r) + (t * color2.r)
				tempColor.g = ((1.0 - t) * color1.g) + (t * color2.g)
				tempColor.b = ((1.0 - t) * color1.b) + (t * color2.b)
				# Bounds check
				tempColor.r = min(255, int(tempColor.r))
				tempColor.g = min(255, int(tempColor.g))
				tempColor.b = min(255, int(tempColor.b))
				# Update LEDs
				led.fill(tempColor)
				led.update()
				end_time = int(round(time.time() * 1000))
				# Update time
				elapsedTimeMs = elapsedTimeMs + (end_time - start_time)

	def animate(self, killEvent):
		while not killEvent.isSet():
			self.color2 = Color(random.randint(32,255), random.randint(32,255), random.randint(32,255))
			self.InterpolateOverTime(self.led, self.color1, self.color2, self.seconds, killEvent)
			self.color1 = self.color2

# Fades from a dim color to a bright color and back
class BreathingLight(BaseAnimationClass):
		def __init__(self, led_strip, color, min_brightness, max_brightness):
				self.base_color = color
				self._min_bright = float(min_brightness)
				self._max_bright = float(max_brightness)
				self._direction = 1
				self._step = 1
				self.led = led_strip

		def scale_brightness(self, step_number):
				return self._min_bright + ((self._max_bright - self._min_bright) * (float(step_number) / 255))

		def step(self, step_amount=1):
				if self._step > 254 or self._step < 0:
						self._direction *= -1

				self.led.fill(
						Color(
								self.base_color.r,
								self.base_color.g,
								self.base_color.b,
								self.scale_brightness(self._step)
						)
				)
				self._step += (1 * self._direction)

		def animate(self, killEvent):
			while not killEvent.isSet():
				self.step()
				self.led.update()

# Same as breathing but color changing in the yellow - pink area
class SexyLight(BaseAnimationClass):
	def __init__(self, led, min_brightness, max_brightness):
		self.led = led
		self.base_color = ColorHSV((random.randint(-60, 45) + 360) % 360, 1.0, 1.0).get_color_rgb()
		self._min_bright = float(min_brightness)
		self._max_bright = float(max_brightness)
		self._direction = 1
		self._step = 1

	def InterpolateOverTime(self, led,color1, color2, seconds, killEvent):
			tempColor = Color(0,0,0)
			elapsedTimeMs = 0
			maxTimeMs = seconds * 1000
			# While we are not done
			while elapsedTimeMs < maxTimeMs:
				# If a change has been requested break out
				if killEvent.isSet():
					break
				# Get the start time
				start_time = int(round(time.time() * 1000))
				# Update color values
				# Simple Linear Interpolate equation: y = (1 - t) * alpha + t * beta
				t = float(elapsedTimeMs) / float(maxTimeMs)
				tempColor.r = ((1.0 - t) * color1.r) + (t * color2.r)
				tempColor.g = ((1.0 - t) * color1.g) + (t * color2.g)
				tempColor.b = ((1.0 - t) * color1.b) + (t * color2.b)
				# Bounds check
				tempColor.r = min(255, int(tempColor.r))
				tempColor.g = min(255, int(tempColor.g))
				tempColor.b = min(255, int(tempColor.b))
				# Update LEDs
				led.fill(tempColor)
				led.update()
				end_time = int(round(time.time() * 1000))
				# Update time
				elapsedTimeMs = elapsedTimeMs + (end_time - start_time)

	def scale_brightness(self, step_number):
		return self._min_bright + ((self._max_bright - self._min_bright) * (float(step_number) / 255))

	def step(self, killEvent, step_amount=1):
		if self._step > 254 or self._step < 0:
			self._direction *= -1

		if self._step < 0:
			newColor = ColorHSV((random.randint(-60, 45) + 360) % 360, 1.0, 1.0).get_color_rgb()
			brightness = self.scale_brightness(self._step)
			self.InterpolateOverTime(self.led, Color(self.base_color.r, self.base_color.g, self.base_color.b, brightness), Color(newColor.r, newColor.g, newColor.b, brightness), 3, killEvent)
			self.base_color = newColor

		self.led.fill(
			Color(
				self.base_color.r,
				self.base_color.g,
				self.base_color.b,
				self.scale_brightness(self._step)
			)
		)
		self._step += (1 * self._direction)

	def animate(self, killEvent):
		while not killEvent.isSet():
			self.step(killEvent)
			self.led.update()

class TimeAnim(BaseAnimationClass):
	def __init__(self, led):
		self.led = led

	def InterpolateOverTime(self, led,color1, color2, seconds, killEvent):
			tempColor = Color(0,0,0)
			elapsedTimeMs = 0
			maxTimeMs = seconds * 1000
			# While we are not done
			while elapsedTimeMs < maxTimeMs:
				# If a change has been requested break out
				if killEvent.isSet():
					break
				# Get the start time
				start_time = int(round(time.time() * 1000))
				# Update color values
				# Simple Linear Interpolate equation: y = (1 - t) * alpha + t * beta
				t = float(elapsedTimeMs) / float(maxTimeMs)
				tempColor.r = ((1.0 - t) * color1.r) + (t * color2.r)
				tempColor.g = ((1.0 - t) * color1.g) + (t * color2.g)
				tempColor.b = ((1.0 - t) * color1.b) + (t * color2.b)
				# Bounds check
				tempColor.r = min(255, int(tempColor.r))
				tempColor.g = min(255, int(tempColor.g))
				tempColor.b = min(255, int(tempColor.b))
				# Update LEDs
				led.fill(tempColor)
				led.update()
				end_time = int(round(time.time() * 1000))
				# Update time
				elapsedTimeMs = elapsedTimeMs + (end_time - start_time)

	def step(self, killEvent, step_amount = 1):
		hourColor = ColorHSV(int(datetime.datetime.now().time().hour) * 15, 1.0, 1.0).get_color_rgb()
		minuteColor = ColorHSV(int(datetime.datetime.now().time().minute) * 6, 1.0, 1.0).get_color_rgb()
		self.InterpolateOverTime(self.led, hourColor, minuteColor, 30, killEvent)
		self.InterpolateOverTime(self.led, minuteColor, hourColor, 30, killEvent)

	def animate(self, killEvent):
		while not killEvent.isSet():
			self.step(killEvent)
			self.led.update()

class SunriseAnim(BaseAnimationClass):
	def __init__(self, led, sunriseTime):
		self.led = led
		self.sunriseTime = sunriseTime
		self.lightTime = sunriseTime.sunrise + datetime.timedelta(minutes = -10)
		print(self.lightTime)
		self.endTIme = sunriseTime.sunrise + datetime.timedelta(hours = 1)

	def InterpolateOverTime(self, led,color1, color2, seconds, killEvent):
			tempColor = Color(0,0,0)
			elapsedTimeMs = 0
			maxTimeMs = seconds * 1000
			# While we are not done
			while elapsedTimeMs < maxTimeMs:
				# If a change has been requested break out
				if killEvent.isSet():
					break
				# Get the start time
				start_time = int(round(time.time() * 1000))
				# Update color values
				# Simple Linear Interpolate equation: y = (1 - t) * alpha + t * beta
				t = float(elapsedTimeMs) / float(maxTimeMs)
				tempColor.r = ((1.0 - t) * color1.r) + (t * color2.r)
				tempColor.g = ((1.0 - t) * color1.g) + (t * color2.g)
				tempColor.b = ((1.0 - t) * color1.b) + (t * color2.b)
				# Bounds check
				tempColor.r = min(255, int(tempColor.r))
				tempColor.g = min(255, int(tempColor.g))
				tempColor.b = min(255, int(tempColor.b))
				# Update LEDs
				led.fill(tempColor)
				led.update()
				end_time = int(round(time.time() * 1000))
				# Update time
				elapsedTimeMs = elapsedTimeMs + (end_time - start_time)

	def step(self, killEvent, step_amount = 1):
		minutesToFadeIn = 10
		minutesToStayLit = 60
		sunColor = Color(255,210,80)
		maxColor = Color(255,255,255)
		if self.lightTime <= datetime.datetime.now():
			print("Kicking off animation")
			self.InterpolateOverTime(self.led, Color(0,0,0), sunColor, minutesToFadeIn * 60, killEvent)
			self.InterpolateOverTime(self.led, sunColor, maxColor, minutesToStayLit * 60, killEvent)
			self.led.fill(Color(0,0,0))
			self.led.update()

	def animate(self, killEvent):
		self.led.fill(Color(0,0,0))
		self.led.update()
		while not killEvent.isSet():
			self.step(killEvent)
			self.led.update()
