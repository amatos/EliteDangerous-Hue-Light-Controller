import logging
import logging.config
from time import sleep

import yaml
from phue import Bridge
from rgbxy import Converter

try:
	import config
except ImportError:
	pass


# noinspection SpellCheckingInspection,PyPep8
class HueLightControl:
	"""Send commands to Hue Bridge.
		Populate config.py with:
			HueIP
			hue_light
	Attributes:
		logger : Object
			Local logger from logging
		star_red : int
			Rgb component of star color
		star_green : int
			rGb component of star color
		star_blue : int
			rgB component of star color
		star_bright : float
			Brightness component of star color
		red : int
			Rgb color component
		green : int
			rGb color component
		blue : int
			rgB color component
		bright : float
			Brightness color component
		ciex : float
			CIE X representation of color
		ciey : float
			CIE Y representation of color
		bridge : object
			Philips Hue bridge object
		color_loop : bool
			If true, the hue bulb cycles an RGB loop
		state : bool
			'True' for on, 'False' for off
		alert_status : str
			Hue alert status.
			Valid options are 'none', 'loop', 'select', 'lselect'
		light : str
			The name of the Hue object on the bridge, defined in
			config.py

	Methods:
		_send_command(self):
			Sends the command to the hue bridge
		_set_status(status='none')


	"""

	def __init__(self, hueLight=''):
		"""Initializes HueLightControl with default values.

		Please note, the default values for CIE XY are set to "white",
			with a brightness of 80%.

		RGB color values:      Star color values:
			red: int                star_red: int
			green: int              star_green: int
			blue: int               star_blue: int
									star_bright: float

		CIE XY values:
			ciex: float
			ciey: float

		Brightness:
			bright: float

		:return: None
		"""
		# Load logging config
		with open('logging.yaml', 'r') as f:
			log_cfg = yaml.safe_load(f.read())
		logging.config.dictConfig(log_cfg)
		self.logger = logging.getLogger('EDHue.HueLight')
		self.star_red = 255
		self.star_green = 255
		self.star_blue = 255
		self.star_bright = 0.8
		self.red = 0
		self.green = 0
		self.blue = 0
		self.bright = 0.8
		self.ciex = 0.3122
		self.ciey = 0.3282
		self.bridge = Bridge()
		self.color_loop = False
		self.state = False
		self.alert_status = 'none'
		self.light = hueLight

		self.logger.debug('Initializing HueLightControl.')
		self.logger.debug('Getting light status.')
		if self.light != '':
			self.state = self.bridge.get_light(light_id=self.light, parameter='on')
		else:
			self.logger.debug('Light undefined.  Unable to control hue light.')
		self.logger.debug('Light status: ' + str(self.state))

	def set_rgb(self, r: int = 0, g: int = 0, b: int = 0, bright: float = 0.8):
		"""Turns on the light with the provided RGB and brightness values.
		Takes RGB + Brightness as params.
		Uses rgbxy.Converter() to set the CIE XY values.
		Then calls _send_command() to execute the change.

		:param r: int value for Red (0-254)
		:param g: int value for Green (0-254)
		:param b: int value for Blue (0-254)
		:param bright: Float value describing brightness (0.0-1.0).  Think of
			it like a percentage.
		:return: nothing
		"""
		self.red = r
		self.green = g
		self.blue = b
		self.bright = bright
		convert = Converter()
		self.ciex, self.ciey = convert.rgb_to_xy(red=self.red,
												 green=self.green,
												 blue=self.blue)
		self._send_command()
		return

	def set_cie(self,
				x: float = 0.3122,
				y: float = 0.3282,
				bright: float = 0.8):
		"""Turns on the light with the provided CIE XY values.
		Takes X, Y, and Brightness
		Then calls _send_command() to execute the change.

		:param x: float value for CIE X
		:param y: float value for CIE Y
		:param bright: Float value describing brightness (0.0-1.0).  Think of
			it like a percentage.
		:return: nothing
		"""
		self.ciex = x
		self.ciey = y
		self.bright = bright
		self._send_command()

	def colorloop(self) -> None:
		self.logger.debug('In colorloop')
		self.logger.debug('Set status to loop')
		self._set_status('loop')
		self.logger.debug('Storing old brightness.')
		old_brightness = self.bright
		self.logger.debug('Old brightness: ' + str(old_brightness))
		self.bright = 1
		self.logger.debug('Sending _send_command')
		self._send_command()
		self.bright = old_brightness
		self._set_status()

	def clear_colorloop(self):
		self.logger.debug('Sending a _send_command to clear the color loop')
		self._set_status()
		self._send_command()

	def _set_status(self, status: str = 'none'):
		"""Populates either color_loop or alert_status
		depending on how it's called.

		If called without parameters, sets:
			color_loop to False
			status to none

		if called with status='none', sets the light to not perform an alert
			effect. (default behavior)
		If called with status='loop', sets the light to cycle through all
			hues using the current brightness and saturation settings.
		If called with status='select', sets the light to perform one
			breathing cycle.
		If called with status='lselect', sets the light to perform breathing
			cycles for 15 seconds, or until _set_status is called with
			status='none'

		:param status: 'none', 'loop', 'select', or 'lselect'
		:return: nothing
		"""
		if status == 'loop':
			self.color_loop = True
		else:
			self.color_loop = False
			self.alert_status = status
		if status == 'select':
			self.bright = 1.0
		elif status == 'lselect':
			self.bright = 1.0
		else:
			self.bright = 0.8

	def light_on(self):
		"""
		Sets the light state to ON.
		calls _send_command() to execute

		:return: nothing
		"""
		self.state = True
		self._send_command()

	def light_off(self):
		"""
		Sets the light state to OFF.
		calls _send_command() to execute

		:return: nothing
		"""
		self.state = False
		self._send_command()

	def set_star(self,
				 r: int = 255,
				 g: int = 255,
				 b: int = 255,
				 bright: float = 0.8):
		"""Sets the values for Star RGB and Brightness
		Takes RGB + Brightness as params.

		:param r: int value for Red (0-254)
		:param g: int value for Green (0-254)
		:param b: int value for Blue (0-254)
		:param bright: Float value describing brightness (0.0-1.0).  Think of
			it like a percentage.
		:return: nothing
		"""
		self.star_red = r
		self.star_blue = b
		self.star_green = g
		self.star_bright = bright
		self.logger.debug('Star RGB: '
						  + str(self.star_red) + ' '
						  + str(self.star_green) + ' '
						  + str(self.star_blue))

	def starlight(self):
		"""Turns on the light with the Star RGB and brightness values.
		Uses rgb_to_cie to set the CIE XY values.
		Then calls _send_command() to execute the change.

		:return: nothing
		"""
		self.logger.debug('In Starlight')

		convert = Converter()
		self.ciex, self.ciey = convert.rgb_to_xy(red=self.star_red,
												 green=self.star_green,
												 blue=self.star_blue)
		self.bright = self.star_bright
		self._send_command()
		return

	def _send_command(self):
		"""Executes a set_light _send_command to the Hue bridge via phue.
		bri takes the bright (float) value and converts it to an
			integer between 0 and 254
		If color_loop is set, runs a color loop until interrupted.
		If alert_status is set to 'select' (a single breathing cycle), then
			we run that cycle 3 times.
		After the _send_command is sent to the Hue bridge, we explicitly turn off
			the color_loop.

		:return: nothing
		"""
		self.logger.debug('In Command')
		bri = int(self.bright * 254)
		counter = 1
		if self.color_loop:
			self.logger.debug('Running a color loop')
			effect = 'colorloop'
		else:
			self.logger.debug('Not running a color loop')
			effect = 'none'

		if self.alert_status == 'select':
			counter = 3

		for count in range(counter):
			self.logger.debug('Sending light _send_command.')
			self.bridge.set_light(light_id=self.light,
								  parameter={'on':     self.state,
											 'xy':     [self.ciex, self.ciey],
											 'bri':    bri,
											 'alert':  self.alert_status,
											 'effect': effect})
		self.color_loop = False


def get_lights(bridge):
	pass

def validate_connection(bridge):
	pass

def initial_connection(bridge):
	pass

def main():
	print('Sanity check: Turn on the light, wait 2s, then turn it off.')
	hue = HueLightControl()
	hue.light_on()
	sleep(2)
	hue.light_off()


if __name__ == '__main__':
	print('Run edhue.py to execute program.')
	main()
