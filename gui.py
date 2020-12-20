import ipaddress
import logging
import logging.config
import os
from time import sleep
import PySimpleGUI as sg

import hue_light
from edhue import configure_logger, EDHue, initialize, save_config
import phue

ELITE_ORANGE = '#f07b05'

def GUI_main():
    def GUI_start(ip, light):
        logger.info('In GUImain - start')
        logger.info('Validating bridge connection.')
        connected = False
        try:
            sg.popup_quick_message('Trying to connect', text_color=ELITE_ORANGE,
                                   font=('euro caps', 32))
            ed_hue = EDHue(ip, light)
            connected = True
        except phue.PhueRequestTimeout:
            logger.error('Unable to talk to the bridge on ip: ' + str(ip))
            sg.PopupError('Unable to talk to the Philips Hue bridge at '
                          + str(ip)
                          + '.  Please verify the IP address or use the scan '
                            'for bridge option in Configure.',
                          title='Connection error')
            return connected
        logger.info('ED Hue is active.  Awaiting events...')
        running = True
        ed_hue.light_on()
        return connected, running

    def GUI_cleanup(ip, light='', connected=False):
        logger.debug('In cleanup')
        if connected:
            if light != '':
                try:
                    ed_hue = EDHue(ip, light)
                    ed_hue.light_off()
                    ed_hue.stop()
                except ConnectionRefusedError:
                    logger.error('Unable to connect to bridge.')
                except phue.PhueRegistrationException:
                    logger.error('Hue Bridge registration error.')
                    logger.info('This bridge has not yet been registered.')
                except phue.PhueRequestTimeout:
                    logger.error('Unable to talk to bridge on ip: ' + str(ip))
        logger.info('See you in the Black, Commander!')
        logger.info('o7')


    def GUI_configure_ui(bridge_IP='0.0.0.0', bridge_light=''):
        logger.debug('In Configure UI')
        logger.debug('Passed in values (if any):')
        logger.debug('  Hue IP:    ' + bridge_IP)
        logger.debug('  Hue Light: ' + bridge_light)

        '''
        Philips Hue Bridge configuration
        '''
        # Define the window's contents
        layout = [[sg.Text('Philips Hue Bridge Configuration')],
                  [sg.Text("Type in your Philips Hue Bridge IP address, or "
                           "press 'Scan for Bridge'\nto discover via mDNS.")],
                  [sg.Text()],
                  [sg.Text('Hue Bridge IP:'),
                   sg.Input(default_text=bridge_IP, key='-HUE_BRIDGE-',
                            enable_events=True)],
                  [sg.Text()],
                  [sg.Button('Ok', bind_return_key=True),
                   sg.Button('Scan for Bridge', key='scan'),
                   sg.Button('Cancel')]]
        # Create the window
        window = sg.Window('Configure Hue Bridge', layout)

        # Display and interact with the Window using an Event Loop
        while True:
            event, values = window.read()

            # See if user wants to quit or window was closed
            if event == sg.WINDOW_CLOSED or event == 'Cancel':
                logger.debug('Cancel selected, or window closed.')
                if event != sg.WINDOW_CLOSED:
                    window.close()
                return bridge_IP, bridge_light
            if event == 'scan':
                logger.debug('Scan selected.')
                ip, host, name, type = hue_light.get_bridge()
                window['-HUE_BRIDGE-'].update(ip)
            if event == 'Ok':
                try:
                    ip = values['-HUE_BRIDGE-']
                    ipaddress.ip_address(ip)
                    logger.debug('Valid IP address given: ' + ip)
                    bridge_IP = ip
                except ValueError:
                    logger.debug('Invalid IP address entered.  '
                                 'Showing error window.')
                    sg.PopupError('Please enter a valid IP address')
                try:
                    sg.popup_quick_message('Trying to connect',
                                           text_color=ELITE_ORANGE,
                                           font=('euro caps', 32))
                    ed_hue = EDHue(bridge_IP)
                    window.close()
                    break
                except phue.PhueRequestTimeout:
                    logger.error('Unable to talk to the bridge on ip: '
                                 + str(bridge_IP))
                    sg.PopupError('Unable to talk to the Philips Hue bridge at '
                                  + str(bridge_IP)
                                  + '.  Please verify the IP address or use '
                                    'the scan for bridge option.',
                                  title='Connection error')
                except phue.PhueRegistrationException:
                    sg.PopupError('This Philips Hue bridge is not yet '
                                  'registered.  Please push the button on the '
                                  'bridge and press OK on the previous window '
                                  'within 30 seconds.')

            # if last character in input element is invalid, remove it
            if event == '-HUE_BRIDGE-' \
                    and values['-HUE_BRIDGE-'] \
                    and values['-HUE_BRIDGE-'][-1] not in '0123456789.:':
                window['-HUE_BRIDGE-'].update(values['-HUE_BRIDGE-'][:-1])

        '''
        Philips Hue Light(s) configuration
        '''
        lights = hue_light.get_lights(bridge_IP)
        light_list = []
        widest = 0
        logger.debug('Determining how wide to make the window.')
        for light in lights:
            light_list.append(light[1])
            width = len(light[1])
            if width > widest:
                widest = width
        logger.debug('Widest element is ' + str(widest) + ' chars long.')

        layout = [[sg.Text('Philips Hue Bridge Configuration')],
                  [sg.Text("Please select a light, and press either OK to "
                           "accept or 'Flash Light' to\nturn the light on "
                           "and off.")],
                  [sg.Text()],
                  [sg.Text('Hue Bridge IP:'),
                   sg.Input(default_text=bridge_IP, key='-HUE_BRIDGE-',
                            disabled_readonly_background_color='#000000',
                            disabled=True)],
                  [sg.Text('Hue Light(s): '),
                   sg.Listbox(values=light_list, default_values=bridge_light,
                              size=((widest + 1),10), key='-HUE_LIGHT-')],
                  [sg.Text()],
                  [sg.Button('Ok', bind_return_key=True),
                   sg.Button('Flash Light', key='Flash'),
                   sg.Button('Cancel')]]
        # Create the window
        window = sg.Window('Configure Hue Light', layout)

        # Display and interact with the Window using an Event Loop
        while True:
            event, values = window.read()
            # See if user wants to quit or window was closed
            if event == sg.WINDOW_CLOSED or event == 'Cancel':
                logger.debug('Cancel selected, or window closed.')
                break
            if event == 'Ok':
                bridge_light = values['-HUE_LIGHT-'][0]
                logger.debug('Light selected: ' + bridge_light)
                break
            if event == 'Flash':
                bridge_light = values['-HUE_LIGHT-'][0]
                logger.debug('Flashing light')
                logger.debug('  IP: ' + str(bridge_IP))
                logger.debug('  Light: ' + str(bridge_light))
                ed_hue.set_light(bridge_light)

                if ed_hue.get_status():
                    logger.debug('Light is on, sending off command.')
                    ed_hue.light_off()
                    sleep(1)
                    ed_hue.light_on()
                else:
                    logger.debug('Light is off, sending on command.')
                    ed_hue.light_on()
                    sleep(1)
                    ed_hue.light_off()

        # Finish up by removing from the screen
        logger.debug('Closing Configure window and returning:')
        logger.debug('  Hue IP:    ' + bridge_IP)
        logger.debug('  Hue Light: ' + bridge_light)
        logger.debug('Saving selected configuration for the future.')
        save_config(bridge=bridge_IP, light=bridge_light)
        window.close()
        logger.debug('Returning to main menu.')
        return bridge_IP, bridge_light

    '''
    GUI MAIN
    '''
    bridge_IP, bridge_light, debug = initialize()
    logging.config.dictConfig(configure_logger())
    # create logger with 'EDHue'
    logger = logging.getLogger('EDHue.GUI')

    logger.info('Starting.')

    connected = False
    ed_hue_status = 'Stopped'
    ed_hue_status_color = 'Red'
    # Define my theme
    sg.LOOK_AND_FEEL_TABLE['EliteTheme'] = {'BACKGROUND': '#000000',  # Black
                                            'TEXT': '#ffffff',        # White
                                            'INPUT': ELITE_ORANGE,
                                            'TEXT_INPUT': '#ffffff',  # White
                                            'SCROLL': ELITE_ORANGE,
                                            'BUTTON': ('white', ELITE_ORANGE),
                                            'PROGRESS': ('white', 'black'),
                                            'BORDER': 1,
                                            'SLIDER_DEPTH': 0,
                                            'PROGRESS_DEPTH': 0,
                                            }

    # Switch to use your newly created theme
    sg.theme('EliteTheme')
    # Call a popup to show what the theme looks like
    # sg.popup_get_text('This how the MyNewTheme custom theme looks')

    # Define the window's contents
    layout = [[sg.Button(key='StartImage',
                         image_filename=os.path.join('assets', 'edlogo2.gif'),
                         pad=(0, 0)),
               sg.Button(button_text='Elite Dangerous Hue Light Sync',
                         key='StartText', font=('euro caps', 38), pad=(0, 0))],
              [sg.Text('Configured Bridge:', justification='right',
                       size=(18, 0)),
               sg.Text(bridge_IP, key='Bridge', justification='left',
                       size=(18, 0))],
              [sg.Text('Configured Light:', justification='right',
                       size=(18, 0)),
               sg.Text(bridge_light, key='Light', justification='left',
                       size=(18, 0))],
              [sg.Text('Status:', justification='right',
                       size=(18, 0)),
               sg.Text(ed_hue_status, key='Light', justification='left',
                       text_color=ed_hue_status_color, size=(18, 0))],
              [sg.Text()],
              [sg.Button('Configure', font=('euro caps', 32),
                         pad=((0, 6), (0, 0))),
               sg.Button('Exit', size=(4, 1), pad=((545, 0), (0, 0)),
                         font=('euro caps', 32))]
              ]
    # Create the window
    window = sg.Window('E:D Hue Light Sync', layout, margins=(25, 25),
                       background_color='#000000', element_justification='c')

    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        if event == 'StartImage' or event == 'StartText':
            if bridge_IP == '' and bridge_light == '':
                sg.popup_error('Both the Philips Hue Bridge and Light source '
                               'must be populated.\n'
                               'Click on configure to set them up.')
            elif bridge_IP == '':
                sg.popup_error('The Philips Hue Bridge must be populated.\n'
                               'Click on configure to set it up.')
            elif bridge_light == '':
                sg.popup_error('The Philips Hue Light source must be '
                               'populated.\n'
                               'Click on configure to set it up.')
            connected, running_status = GUI_start(bridge_IP, bridge_light)
        if event == 'Configure':
            window.hide()
            bridge_IP, bridge_light = GUI_configure_ui(bridge_IP, bridge_light)
            window.un_hide()
            window.force_focus()
            logger.debug('Returned bridge IP: ' + bridge_IP)
            logger.debug('Returned Light: ' + bridge_light)
            window['Bridge'].update(bridge_IP)
            window['Light'].update(bridge_light)
        if running_status:
            ed_hue_status = 'Running'
            ed_hue_status_color = 'Green'
            # Define the window's contents
            layout = [[sg.Button(key='StartImage',
                                 image_filename=os.path.join('assets', 'edlogo2.gif'),
                                 pad=(0, 0)),
                       sg.Button(button_text='Elite Dangerous Hue Light Sync',
                                 key='StartText', font=('euro caps', 38), pad=(0, 0))],
                      [sg.Text('Configured Bridge:', justification='right',
                               size=(18, 0)),
                       sg.Text(bridge_IP, key='Bridge', justification='left',
                               size=(18, 0))],
                      [sg.Text('Configured Light:', justification='right',
                               size=(18, 0)),
                       sg.Text(bridge_light, key='Light', justification='left',
                               size=(18, 0))],
                      [sg.Text('Status:', justification='right',
                               size=(18, 0)),
                       sg.Text(ed_hue_status, key='Light', justification='left',
                               text_color=ed_hue_status_color, size=(18, 0))],
                      [sg.Text()],
                      [sg.Button('Configure', font=('euro caps', 32),
                                 pad=((0, 6), (0, 0))),
                       sg.Button('Exit', size=(4, 1), pad=((545, 0), (0, 0)),
                                 font=('euro caps', 32))]
                      ]
            # rereate the window
            window.close()
            window = sg.Window('E:D Hue Light Sync', layout, margins=(25, 25),
                               background_color='#000000',
                               element_justification='c')
    # Finish up by removing from the screen and doing some cleanup
    window.close()
    if connected:
        non_blocking=True
    else:
        non_blocking=False
    sg.popup_auto_close('See you in the Black, Commander.\n\no7',
                        background_color='#000000', text_color=ELITE_ORANGE,
                        no_titlebar=True, button_type=5, font=('euro caps', 32),
                        non_blocking=non_blocking, auto_close_duration=5)
    GUI_cleanup(ip=bridge_IP, light=bridge_light, connected=connected)


if __name__ == '__main__':
    GUI_main()
