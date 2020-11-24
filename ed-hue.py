import config
import glob
import json
import logging
import math
import os
import psutil
import subprocess
import tkinter as tk
import threading
from threading import Thread
from time import sleep
from hue_light import hue_light_control


def cleanup():
    print('Turning off ' + config.hueLight)
    print(hue.state)
    hue.light_off()
    print(hue.state)

    main.destroy()
    print('See you in the Black, Commander!')
    print('o7')


def get_journal_entries(hue):
    list_of_files = glob.glob(config.logLocation)
    try:
        latest_file = max(list_of_files, key=os.path.getctime)
        
        print(latest_file)

        # open latest log
        currentLog = open(latest_file, 'r')

        while True:
            # reads lines
            reader = currentLog.read().splitlines()

            # checks if any events exist
            if len(reader) != 0:
                # gets last line of log (most recent event)
                parse_journal_json(hue, reader[-1])
            sleep(0.25)
    except KeyboardInterrupt:
        print("Done.")

    return

def parse_journal_json(hue, line):
    # Alert types
    flash = 'select'
    alarm = 'lselect'
    journal_event = json.loads(line)

    if journal_event['event'] == 'Scan' and journal_event['ScanType'] == 'AutoScan' and journal_event['BodyID'] == 0:
        print('Autoscan on system arrival.  Setting light for star type ' + journal_event['StarType'])
        r, g, b, bri, sat = star_color(journal_event['StarType'])
        # Take the submitted brightness value, convert it to a float between 0 and 1, and decrease it by 20%
        bri = (bri/254) * 0.8
        print('Star light values: r: ' + str(r) + ' g:' + str(g) + ' b:' + str(b) + ' Brightness:' + str(bri))
        hue.set_rgb(r = r, g=g, b=b, bright=bri)

    elif journal_event['event'] == 'ShieldState':
        if journal_event['event'] == 'ShieldsUp':
            print('Shield on')
            # flash silver
            hue.set_status(flash)
            hue.set_rgb(r = 192, g=192, b=192)
            hue.set_status()
        else:
            print('Shield Off')
            # flash orange
            hue.set_status(flash)
            hue.set_rgb(r = 255, g=165, b=0)
            hue.set_status()
    elif journal_event['event'] in ('Docked', 'Shutdown'):
        print('docked')
        # Set hue to bright white
        hue.set_rgb(r = 255, g=255, b=255)
    elif journal_event['event'] == 'Undocked':
        print('Undocked')
        # flash silver
        hue.set_status(flash)
        hue.set_rgb(r = 192, g=192, b=192)
        hue.set_status()
    elif journal_event['event'] == 'DockingGranted':
        print('Docking granted')
        # flash green
        hue.set_status(flash)
        hue.set_rgb(r = 0, g=128, b=0, bright=0.5)
        hue.set_status()
    elif journal_event['event'] == 'PVPKill':
        print('PVP Kill!')
        # flash green
        hue.set_status(flash)
        hue.set_rgb(r = 0, g=255, b=0)
        hue.set_status()
    elif journal_event['event'] == 'SupercruiseEntry':
        print('Entering Supercruise')
        # flash yellow
        hue.set_status(flash)
        hue.set_rgb(r = 255, g=255, b=0)
        hue.set_status()
    elif journal_event['event'] == 'SupercruiseExit':
        print('Exiting Supercruise')
        # flash blue
        hue.set_status(flash)
        hue.set_rgb(r = 0, g=0, b=255)
        hue.set_status()
    elif journal_event['event'] in ('UnderAttack', 'HullDamage', 'HeatDamage'):
        print('Damaged, or under attack')
        # flash red
        hue.set_status(flash)
        hue.set_rgb(r = 255, g=0, b=0)
        hue.set_status()
    elif journal_event['event'] == 'HeatWarning':
        print('Getting warm in the cabin')
        # flash red
        hue.set_status(flash)
        hue.set_rgb(r = 255, g=165, b=0)
        hue.set_status()
    elif journal_event['event'] == 'StartJump':
        print('FSD Jump')
        # Cycle through a color loop
        hue.set_status('loop')
        hue.set_rgb(r = 255, g=255, b=255)
        hue.set_status()
    else:
        print('Nothing found.')

    return

def start():
    print('Welcome!')
    print(hue.state)
    hue.light_on()
    print(hue.state)

    # x = threading.Thread(target=parse_journal_entries, args=(huebridge,), daemon=True)
    x = Thread(target=get_journal_entries, args=(hue,), daemon=True)
    x.start()


def star_color(star_class: str):
    # Main Sequence Stars
    star_class_O = { 'red': 155, 'green': 176, 'blue': 255, 'brightness': 254, 'saturation': 254 }
    star_class_B = { 'red': 170, 'green': 191, 'blue': 255, 'brightness': 254, 'saturation': 254 }
    star_class_A = { 'red': 202, 'green': 215, 'blue': 255, 'brightness': 254, 'saturation': 254 }
    star_class_F = { 'red': 248, 'green': 247, 'blue': 255, 'brightness': 254, 'saturation': 254 }
    star_class_G = { 'red': 255, 'green': 244, 'blue': 234, 'brightness': 254, 'saturation': 254 }
    star_class_K = { 'red': 255, 'green': 210, 'blue': 161, 'brightness': 254, 'saturation': 254 }
    star_class_M = { 'red': 255, 'green': 204, 'blue': 111, 'brightness': 190, 'saturation': 200 }
    star_class_L = { 'red': 255, 'green': 50, 'blue': 80, 'brightness': 150, 'saturation': 254 }
    star_class_T = { 'red': 148, 'green': 16, 'blue': 163, 'brightness': 254, 'saturation': 254 }
    star_class_Y = { 'red': 148, 'green': 16, 'blue': 163, 'brightness': 100, 'saturation': 254 }
    # Proto Stars
    star_class_TTS = { 'red': 255, 'green': 204, 'blue': 111, 'brightness': 150, 'saturation': 150 }
    star_class_AeBe = { 'red': 202, 'green': 215, 'blue': 255, 'brightness': 105, 'saturation': 150 }
    # Neutron Star
    star_class_N = { 'red': 155, 'green': 176, 'blue': 255, 'brightness': 254, 'saturation': 254}
    star_class_H = { 'red': 1, 'green': 1, 'blue': 1, 'brightness': 0, 'saturation': 0 }
    star_class_SupermassiveBlackHole = { 'red': 255, 'green': 255, 'blue': 255, 'brightness': 20, 'saturation': 5 }
    star_class_M_RedSuperGiant = { 'red': 255, 'green': 204, 'blue': 111, 'brightness': 254, 'saturation': 254 }

    if star_class == "O":
        red = star_class_O['red']
        green = star_class_O['green']
        blue = star_class_O['blue']
        bri = star_class_O['brightness']
        sat = star_class_O['saturation']
    elif star_class == "B":
        red = star_class_B['red']
        green = star_class_B['green']
        blue = star_class_B['blue']
        bri = star_class_B['brightness']
        sat = star_class_B['saturation']
    elif star_class == "A":
        red = star_class_A['red']
        green = star_class_A['green']
        blue = star_class_A['blue']
        bri = star_class_A['brightness']
        sat = star_class_A['saturation']
    elif star_class == "F":
        red = star_class_F['red']
        green = star_class_F['green']
        blue = star_class_F['blue']
        bri = star_class_F['brightness']
        sat = star_class_F['saturation']
    elif star_class == "G":
        red = star_class_G['red']
        green = star_class_G['green']
        blue = star_class_G['blue']
        bri = star_class_G['brightness']
        sat = star_class_G['saturation']
    elif star_class == "K":
        red = star_class_K['red']
        green = star_class_K['green']
        blue = star_class_K['blue']
        bri = star_class_K['brightness']
        sat = star_class_K['saturation']
    elif star_class == "M":
        red = star_class_M['red']
        green = star_class_M['green']
        blue = star_class_M['blue']
        bri = star_class_M['brightness']
        sat = star_class_M['saturation']
    elif star_class == "L":
        red = star_class_L['red']
        green = star_class_L['green']
        blue = star_class_L['blue']
        bri = star_class_L['brightness']
        sat = star_class_L['saturation']
    elif star_class == "T":
        red = star_class_T['red']
        green = star_class_T['green']
        blue = star_class_T['blue']
        bri = star_class_T['brightness']
        sat = star_class_T['saturation']
    elif star_class == "Y":
        red = star_class_Y['red']
        green = star_class_Y['green']
        blue = star_class_Y['blue']
        bri = star_class_Y['brightness']
        sat = star_class_Y['saturation']
    elif star_class == "TTS":
        red = star_class_TTS['red']
        green = star_class_TTS['green']
        blue = star_class_TTS['blue']
        bri = star_class_TTS['brightness']
        sat = star_class_TTS['saturation']
    elif star_class == "AeBe":
        red = star_class_AeBe['red']
        green = star_class_AeBe['green']
        blue = star_class_AeBe['blue']
        bri = star_class_AeBe['brightness']
        sat = star_class_AeBe['saturation']
    elif star_class == "N":
        red = star_class_N['red']
        green = star_class_N['green']
        blue = star_class_N['blue']
        bri = star_class_N['brightness']
        sat = star_class_N['saturation']
    elif star_class == "H":
        red = star_class_H['red']
        green = star_class_H['green']
        blue = star_class_H['blue']
        bri = star_class_H['brightness']
        sat = star_class_H['saturation']
    elif star_class == "SupermassiveBlackHole":
        red = star_class_SupermassiveBlackHole['red']
        green = star_class_SupermassiveBlackHole['green']
        blue = star_class_SupermassiveBlackHole['blue']
        bri = star_class_SupermassiveBlackHole['brightness']
        sat = star_class_SupermassiveBlackHole['saturation']
    elif star_class == "M_RedSuperGiant":
        red = star_class_M_RedSuperGiant['red']
        green = star_class_M_RedSuperGiant['green']
        blue = star_class_M_RedSuperGiant['blue']
        bri = star_class_M_RedSuperGiant['brightness']
        sat = star_class_M_RedSuperGiant['saturation']
    
    return red, green, blue, bri, sat


# def setupBridgeUI():
#     # Try to connect to Hue lights
#     huebridge = None
#     setup = tk.Tk()
#     setup.title("Set up Hue bridge.")
#     setup.geometry("700x200")
#     setup.configure(background = "#000000")
 
#     tk.Label(setup, text = "Scanning for available mDNS hue bridges", bg = "#000000", fg = "#f07b05", font = ("euro caps", 24)).pack()
    
#     # print("Scanning for available mDNS hue bridges")
#     _, available_devices = find_mdns_huebridge_devices()

#     for this_device in available_devices:
#         # print("Found Device: {} - Board {} - Branch {} - Revision {}".format(this_device['mDNSname'],
#         #                                                                      this_device['board'],
#         #                                                                      this_device['branch'],
#         #                                                                      this_device['revision']))
#         print("Found Device: {}".format(this_device['mDNSname'],))
#         huebridge = this_device['mDNSname'] + '.local'
#     print('Bridge: ' + huebridge)


if __name__ == '__main__':
    hue = hue_light_control()
    # gui setup
    main = tk.Tk()

    main.title("Elite Dangerous Hue Light Sync")
    main.geometry("800x300")
    main.configure(background = "#000000")

    # logo image
    edlogo = tk.PhotoImage(file = "assets\edlogo2.gif")

    # gui
    tk.Label(main, text = "Elite Dangerous Hue Light Sync", bg = "#000000", fg = "#f07b05", font = ("euro caps", 38)).pack()
    tk.Label(main, bg = "#000000").pack()
    # Label(main, text = "Created by Hector Robe", bg = "#000000", fg = "#f07b05", bd = "0", font = ("sintony", 12)).pack()
    # Label(main, bg = "#000000").pack()
    tk.Button(main, compound = tk.LEFT, image = edlogo, borderwidth = 0, highlightthickness = 0, 
        pady = 0, padx = 10, text = "Start Lighting", relief = tk.SOLID, command = start, 
        bg = "#f07b05", fg = "#ffffff", font = ("euro caps", 32)).pack()
    tk.Label(main, bg = "#000000").pack()
    # tk.Button(main, borderwidth = 0, highlightthickness = 0, pady = 0, padx = 10, 
    #        text = "Set up Hue bridge", relief = tk.SOLID, command = setupBridgeUI, bg = "#f07b05", 
    #        fg = "#ffffff", font = ("euro caps", 32)).pack()
    main.protocol("WM_DELETE_WINDOW", cleanup)

    # gui setup
    main.mainloop()