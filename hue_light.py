import logging
import logging.config
from time import sleep

import phue
import yaml
from rgbxy import Converter

import mdns
from log import configure_logger

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

    def __init__(self, hue_IP, hue_light=''):
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
        logging.config.dictConfig(configure_logger())
        self.logger = logging.getLogger('EDHue.HueLight')
        self.logger.debug('Initializing HueLightControl')
        self.star_red = 255
        self.star_green = 255
        self.star_blue = 255
        self.star_bright = 0.8
        self.red = 1
        self.green = 1
        self.blue = 1
        self.bright = 0.8
        self.ciex = 0.3122
        self.ciey = 0.3282
        self.color_loop = False
        self.state = False
        self.alert_status = 'none'
        self.light = hue_light

        try:
            self.logger.debug('Trying to connect to Hue bridge')
            self.validate_connection(hue_IP)
            self.bridge = phue.Bridge(hue_IP)
        except phue.PhueRequestTimeout:
            self.logger.debug('Failed to connect to Hue bridge')
            raise
        self.logger.debug('Getting light status.')
        if self.light != '':
            self.logger.debug('Light object: ' + str(self.light))
            self.state = self.bridge.get_light(light_id=self.light, parameter='on')
            self.logger.debug('Light status: ' + str(self.state))
        else:
            self.logger.debug("Light undefined.  Unable to control hue light.\n"
                              "n.b.: This is expected if a light hasn't been "
                              "selected yet.")

    def get_status(self):
        self.logger.debug('Getting light status.')
        self.logger.debug('  light: ' + str(self.light))
        status = self.bridge.get_light(light_id=self.light, parameter='on')
        return status

    def get_current_colors(self):
        ciex, ciey = self.bridge.get_light(light_id=self.light, parameter='xy')
        bright = self.bridge.get_light(light_id=self.light, parameter='bri')
        return ciex, ciey, bright

    def set_rgb(self, r: int = 1, g: int = 1, b: int = 1, bright: float = 0.8):
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
        self.ciex, self.ciey = self.convert_rgb()
        self._send_command()
        return

    def convert_rgb(self, red=255, green=255, blue=255):
        if red == 255:
            red = self.red
        if green == 255:
            green = self.green
        if blue == 255:
            blue = self.blue
        self.logger.debug('Converting rgb values')
        self.logger.debug('  red   : ' + str(red))
        self.logger.debug('  green : ' + str(green))
        self.logger.debug('  blue  : ' + str(blue))
        convert = Converter()
        ciex, ciey = convert.rgb_to_xy(red=red,
                                       green=green,
                                       blue=blue)
        self.logger.debug('Resulting ciex/ciey:')
        self.logger.debug('  ciex: ' + str(ciex))
        self.logger.debug('  ciey: ' + str(ciey))
        return ciex, ciey

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
        self.logger.debug('Turning light on')
        self.state = True
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
        self.logger.debug('  red   : ' + str(self.star_red))
        self.logger.debug('  green : ' + str(self.star_green))
        self.logger.debug('  blue  : ' + str(self.star_blue))
        self.logger.debug('Turn on the light')
        self.state = True
        self.logger.debug('Converting RGB to ciex/ciey')
        self.ciex, self.ciey = self.convert_rgb(red=self.star_red,
                                                green=self.star_green,
                                                blue=self.star_blue)
        self.bright = self.star_bright
        self._send_command()
        return

    def alert_light(self,
                    r: int = 255,
                    g: int = 255,
                    b: int = 255,
                    bright: float = 1):
        self.logger.debug('In alert_light')
        current_ciex, current_ciey, current_bright = self.get_current_colors()
        self.logger.debug('Alert colors:')
        self.logger.debug('  red    : ' + str(r))
        self.logger.debug('  green  : ' + str(g))
        self.logger.debug('  blue   : ' + str(b))
        self.logger.debug('  bright : ' + str(bright))
        self.red = r
        self.green = g
        self.blue = b
        self.bright = bright
        self.ciex, self.ciey = self.convert_rgb()
        self.alert_status = 'select'
        self.logger.debug('Current ciex/ciey    : [' + str(current_ciex)
                          + ', ' + str(current_ciey) + ']')
        self.logger.debug('alert ciex/ciey      : [' + str(self.ciex)
                          + ', ' + str(self.ciey) + ']')
        self._send_command()
        self.ciex = current_ciex
        self.ciey = current_ciey
        self.bright = current_bright
        self.alert_status = 'none'
        self.logger.debug('Reverted to ciex/ciey: [' + str(self.ciex)
                          + ', ' + str(self.ciey) + ']')
        self._send_command()

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
        self.logger.debug('In _send_command')
        bri = int(self.bright * 254)
        counter = 1
        if self.color_loop:
            self.logger.debug('Running a color loop')
            effect = 'colorloop'
        else:
            self.logger.debug('Not running a color loop')
            effect = 'none'

        if self.alert_status == 'select':
            self.logger.debug('Alert status was select')
            counter = 10

        for count in range(counter):
            if counter > 1:
                self.logger.debug('Sending light _send_command '
                                  + str(count + 1) + '/' + str(counter))
                self.logger.debug('Sleeping for 1 second')
                sleep(1)
            else:
                self.logger.debug('Sending light _send_command.')
            self.logger.debug('  state : ' + str(self.state))
            self.logger.debug('  xy    : ' + str([self.ciex, self.ciey]))
            self.logger.debug('  bri   : ' + str(bri))
            self.logger.debug('  alert : ' + str(self.alert_status))
            self.logger.debug('  effect: ' + str(effect))
            self.bridge.set_light(light_id=self.light,
                                  parameter={'on': self.state,
                                             'xy': [self.ciex, self.ciey],
                                             'bri': bri,
                                             'alert': self.alert_status,
                                             'effect': effect})
        self.color_loop = False

    def validate_connection(self, bridge):
        self.logger.debug('In validate_connection')
        try:
            hue_bridge = phue.Bridge(ip=bridge)
        except phue.PhueRequestTimeout:
            self.logger.error('Request timed out talking to Hue Bridge at ' + bridge + '.')
            raise
        except phue.PhueRegistrationException:
            self.logger.error('Press the hue button')
            raise
        self.logger.debug('Connection established to ' + str(bridge))


def get_bridge():
    # Load logging config
    logging.config.dictConfig(configure_logger())
    logger = logging.getLogger('EDHue.HueLight.validation')
    ip = ''
    host = ''
    name = ''
    mdns_type = ''
    logger.debug('In get_bridge')
    logger.debug('Calling mdns to find a bridge.')
    logger.debug('n.b.: This can take up to 5 seconds before we time out,')
    logger.debug('      and, we will try 3 times before giving up.')
    for counter in range(3):
        ip, host, name, mdns_type = mdns.mdns_search()
        if ip != '':
            break
        else:
            logger.debug('Bridge not found.  Retrying up to '
                         + str(2 - counter) + 'more times.')
    return ip, host, name, mdns_type


def get_lights(bridge):
    # Load logging config
    logging.config.dictConfig(configure_logger())
    logger = logging.getLogger('EDHue.HueLight.validation')
    logger.debug('In get_lights')
    lights = []
    light_objects = phue.Bridge(bridge).get_light_objects(mode='id')
    for count in light_objects:
        light = (light_objects[count].light_id, light_objects[count].name)
        lights.append(light)
    return lights


if __name__ == '__main__':
    print('Run edhue.py to execute program.')
    ip, hostname, name, mdns_type = get_bridge()
    print('Hue bridge found (if any) at:')
    print('  name:     ' + name)
    print('  mdns_type:     ' + mdns_type)
    print('  hostname: ' + hostname)
    print('  IP:       ' + str(ip))
