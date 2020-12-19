import ipaddress
import logging
import logging.config
import os

import PySimpleGUI as sg

from edhue import configure_logger, EDHue, initialize
from hue_light import HueLightControl
import mdns

def GUImain():
    def start(hue_light):
        logger.info('Starting.')
        hue = HueLightControl(hue_light)
        EDHue(hue_light)
        logger.info('ED Hue is active.  Awaiting events...')
        hue.light_on()

    def cleanup(hue_light):
        if hue_light != '':
            hue = HueLightControl(hue_light)
            hue.light_off()
        logger.info('See you in the Black, Commander!')
        logger.info('o7')
        EDHue(hue_light).stop()

    def configure_ui(hue_IP='0.0.0.0', hue_light=''):
        logger.debug('In Configure UI')
        logger.debug('Passed in values (if any):')
        logger.debug('  Hue IP:    ' + hue_IP)
        logger.debug('  Hue Light: ' + hue_light)

        # Define the window's contents
        layout = [[sg.Text('Philips Hue Bridge Configuration')],
                  [sg.Text('Hue Bridge IP:'), sg.Input(default_text=hue_IP, key='-HUE_BRIDGE-', enable_events=True)],
                  [sg.Button('Ok', bind_return_key=True), sg.Button('Scan for Bridge', key='scan'), sg.Button('Cancel')]]
        # Create the window
        window = sg.Window('Configure Hue Bridge', layout)

        # Display and interact with the Window using an Event Loop
        while True:
            event, values = window.read()
            # See if user wants to quit or window was closed
            if event == sg.WINDOW_CLOSED or event == 'Cancel':
                logger.debug('Cancel selected, or window closed.')
                break
            if event == 'scan':
                ip, host, name, type = mdns.mdns_search()
                window['-HUE_BRIDGE-'].update(ip)
            if event == 'Ok':
                try:
                    ipaddress.ip_address(values['-HUE_BRIDGE-'])
                    logger.debug('Valid IP address given: ' + values['-HUE_BRIDGE-'])
                    hue_IP = values['-HUE_BRIDGE-']
                    break
                except ValueError:
                    logger.debug('Invalid IP address entered.  Showing error window.')
                    sg.PopupError('Please enter a valid IP address')

            # if last character in input element is invalid, remove it
            if event == '-HUE_BRIDGE-' and values['-HUE_BRIDGE-'] and values['-HUE_BRIDGE-'][-1] not in ('0123456789.:'):
                window['-HUE_BRIDGE-'].update(values['-HUE_BRIDGE-'][:-1])

        layout = [[sg.Text('Philips Hue Bridge Configuration')],
                  [sg.Text('Hue Bridge IP:'), sg.Input(default_text=hue_IP, key='-HUE_BRIDGE-',
                                                       disabled_readonly_background_color='#000000', disabled=True)],
                  [sg.Text('Hue Light(s): '),
                   sg.Input(default_text=hue_light, key='-HUE_LIGHT-', pad=((10, 0), (10, 10)))],
                  [sg.Button('Ok', bind_return_key=True), sg.Button('Scan for Lights', key='scan'), sg.Button('Cancel')]]

        window = sg.Window('Configure Hue Light', layout)

        # Display and interact with the Window using an Event Loop
        while True:
            event, values = window.read()
            # See if user wants to quit or window was closed
            if event == sg.WINDOW_CLOSED or event == 'Cancel':
                logger.debug('Cancel selected, or window closed.')
                break
            if event == 'Ok':
                hue_light = values['-HUE_LIGHT-']
                break
            if event == 'scan':

                break

        # Finish up by removing from the screen
        logger.debug('Closing Configure window and returning:')
        logger.debug('  Hue IP:    ' + hue_IP)
        logger.debug('  Hue Light: ' + hue_light)
        window.close()
        return hue_IP, hue_light

    bridgeIP, bridgeLight, debug = initialize()
    configure_logger()
    # create logger with 'EDHue'
    logger = logging.getLogger('EDHue.GUI')

    logger.info('Starting.')

    # Define my theme
    sg.LOOK_AND_FEEL_TABLE['EliteTheme'] = {'BACKGROUND': '#000000',    # Black
                                            'TEXT': '#ffffff',          # White
                                            'INPUT': '#f07b05',         # Elite Orange
                                            'TEXT_INPUT': '#ffffff',    # White
                                            'SCROLL': '#f07b05',        # Elite Orange
                                            'BUTTON': ('white', '#f07b05'), # White on Elite Orange
                                            'PROGRESS': ('#ffffff', '#000000'), # White on Black
                                            'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                            }

    # Switch to use your newly created theme
    sg.theme('EliteTheme')
    # Call a popup to show what the theme looks like
    # sg.popup_get_text('This how the MyNewTheme custom theme looks')

    # Define the window's contents
    layout = [[sg.Button(key='StartImage', image_filename=os.path.join('assets', 'edlogo2.gif'), pad=(0, 0)),
               sg.Button(button_text='Elite Dangerous Hue Light Sync', key='StartText', font=('euro caps', 38),
                         pad=(0, 0))],
              [sg.Text('Configured Bridge:', justification='right', size=(18, 0)),
               sg.Text(bridgeIP, key='Bridge', justification='left', size=(18, 0))],
              [sg.Text('Configured Light:', justification='right', size=(18, 0)),
               sg.Text(bridgeLight, key='Light', justification='left', size=(18, 0))],
              [sg.Button('Configure', font=('euro caps', 32), pad=((0, 6), (0, 0))),
               sg.Button('Exit', size=(4, 1), pad=((545, 0), (0, 0)), font=('euro caps', 32))]
              ]
    # Create the window
    window = sg.Window('E:D Hue Light Sync', layout, margins=(25, 25), background_color='#000000',
                       element_justification='c')

    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        if event == 'StartImage' or event == 'StartText':
            if bridgeIP == '' and bridgeLight == '':
                sg.popup_error('Both the Philips Hue Bridge and Light source must be populated.\n'
                               'Click on configure to set them up.')
            elif bridgeIP == '':
                sg.popup_error('The Philips Hue Bridge must be populated.\n'
                               'Click on configure to set it up.')
            elif bridgeLight == '':
                sg.popup_error('The Philips Hue Light source must be populated.\n'
                               'Click on configure to set it up.')

            start(window.AllKeysDict['Light'].DisplayText)
        if event == 'Configure':
            window.hide()
            bridgeIP, bridgeLight = configure_ui(bridgeIP, bridgeLight)
            window.un_hide()
            logger.debug('Returned bridge IP: ' + bridgeIP)
            logger.debug('Returned Light: ' + bridgeLight)
            window['Bridge'].update(bridgeIP)
            window['Light'].update(bridgeLight)
    # Finish up by removing from the screen and doing some cleanup
    window.close()
    sg.popup_auto_close('See you in the Black, Commander.\n\no7', background_color='#000000', text_color='#f07b05',
                        no_titlebar=True, button_type=5, font=('euro caps', 32))
    cleanup(window.AllKeysDict['Light'].DisplayText)


if __name__ == '__main__':
    GUImain()
