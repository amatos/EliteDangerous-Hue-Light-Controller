import config
import logging
from time import sleep
from phue import Bridge
from rgbxy import Converter


logger = logging.getLogger('EDHue.HueLight')


class hue_light_control:
    """Controls a Hue Light (or lights, or group) via a Hue Bridge
        Populate config.py with:
            HueIP
            hueLight
    """
    def __init__(self):
        """
        Initializes hue_light_control with some default values.

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

        ::return: nothing
        """
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
        self.light = config.hueLight

        logger.debug('Initializing hue_light_control.')
        logger.debug('Getting light status.')
        self.state = self.bridge.get_light(light_id=self.light, parameter='on')
        logger.debug('Light status: ' + str(self.state))

    def rgb_to_cie(self):
        """Takes the values in red, green, blue, and populates the CIE XY equivalents
            Based on Philips implementation guidance:
            http://www.developers.meethue.com/documentation/color-conversions-rgb-xy

        :return: nothing
        """
        convert = Converter()
        self.ciex, self.ciey = convert.rgb_to_xy(red=self.red, green=self.green, blue=self.blue)
        return
        
    def set_rgb(self, r: int=0, g: int=0, b: int=0, bright: float=0.8):
        """
        Turns on the light with the provided RGB and brightness values.
        Takes RGB + Brightness as params.
        Uses rgb_to_cie to set the CIE XY values.
        Then calls command() to execute the change.

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
        self.rgb_to_cie()
        self.bright = bright
        self.rgb_to_cie()
        self.command()
        return

    def set_cie(self, x: float=0.3122, y: float=0.3282, bright: float=0.8):
        """
        Turns on the light with the provided CIE XY values.
        Takes X, Y, and Brightness
        Then calls command() to execute the change.

        :param x: float value for CIE X
        :param y: float value for CIE Y
        :param bright: Float value describing brightness (0.0-1.0).  Think of
                       it like a percentage.
        :return: nothing
        """ 
        self.ciex = x
        self.ciey = y
        self.bright = bright
        self.command()
    
    def colorloop(self):
        logger.debug('In colorloop')
        logger.debug('Set status to loop')
        self.set_status('loop')
        logger.debug('Storing old brightness.')
        old_brightness = self.bright
        logger.debug('Old brightness: ' + str(old_brightness))
        self.bright = 1
        logger.debug('Sending command')
        self.command()
        self.bright = old_brightness
        self.set_status()
    
    def clear_colorloop(self):
        logger.debug('Sending a command to clear the color loop')
        self.set_status()
        self.command()

    def set_status(self, status: str='none'):
        """
        set_status populates either color_loop or alert_status
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
            cycles for 15 seconds, or until set_status is called with
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
        calls command() to execute
        
        :return: nothing
        """
        self.state = True
        self.command()

    def light_off(self):
        """
        Sets the light state to OFF.
        calls command() to execute
        
        :return: nothing
        """
        self.state = False
        self.command()

    def set_star(self, r: int=255, g: int=255, b: int=255, bright: float=0.8):
        """
        Sets the values for Star RGB and Brightness
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
        logger.debug('Star RGB: ' + str(self.star_red) + ' ' + str(self.star_green) + ' ' + str(self.star_blue))

    def starlight(self):
        """
        Turns on the light with the Star RGB and brightness values.
        Uses rgb_to_cie to set the CIE XY values.
        Then calls command() to execute the change.

        :return: nothing
        """
        logger.debug('In Starlight')

        convert = Converter()
        self.ciex, self.ciey = convert.rgb_to_xy(red=self.star_red, green=self.star_green, blue=self.star_blue)
        self.bright = self.star_bright
        self.command()

    def command(self):
        """
        Executes a set_light command to the Hue bridge via phue.
        bri takes the bright (float) value and converts it to an
            integer between 0 and 254
        If color_loop is set, runs a color loop until interrupted.
        If alert_status is set to 'select' (a single breathing cycle), then
            we run that cycle 3 times.
        After the command is sent to the Hue bridge, we explicitly turn off
            the color_loop.
        
        :return: nothing
        """
        logger.debug('In Command')
        bri = int(self.bright * 254)
        counter = 1
        if self.color_loop:
            logger.debug('Running a color loop')
            effect = 'colorloop'
        else:
            logger.debug('Not running a color loop')
            effect = 'none'

        if self.alert_status == 'select':
            counter = 3
        
        for count in range(counter):
            logger.debug('Sending light command.')
            self.bridge.set_light(light_id=self.light, parameter={'on': self.state, 'xy':[self.ciex, self.ciey], 'bri': bri, 'alert': self.alert_status, 'effect': effect})
        self.color_loop = False

if __name__ == '__main__':
    hue = hue_light_control()
    hue.light_on()
    sleep(2)
    hue.light_off()
