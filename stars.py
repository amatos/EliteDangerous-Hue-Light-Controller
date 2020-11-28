def star_color(star_class: str = ''):
	# Main Sequence Stars
	star_class_O = {'red': 155, 'green': 176, 'blue': 255, 'brightness': 254, 'saturation': 254}
	star_class_B = {'red': 170, 'green': 191, 'blue': 255, 'brightness': 254, 'saturation': 254}
	star_class_A = {'red': 202, 'green': 215, 'blue': 255, 'brightness': 254, 'saturation': 254}
	star_class_F = {'red': 248, 'green': 247, 'blue': 255, 'brightness': 254, 'saturation': 254}
	star_class_G = {'red': 255, 'green': 244, 'blue': 234, 'brightness': 254, 'saturation': 254}
	star_class_K = {'red': 255, 'green': 210, 'blue': 161, 'brightness': 254, 'saturation': 254}
	star_class_M = {'red': 255, 'green': 204, 'blue': 111, 'brightness': 190, 'saturation': 200}
	star_class_L = {'red': 255, 'green': 50, 'blue': 80, 'brightness': 150, 'saturation': 254}
	star_class_T = {'red': 148, 'green': 16, 'blue': 163, 'brightness': 254, 'saturation': 254}
	star_class_Y = {'red': 148, 'green': 16, 'blue': 163, 'brightness': 100, 'saturation': 254}
	# Proto Stars
	star_class_TTS = {'red': 255, 'green': 204, 'blue': 111, 'brightness': 150, 'saturation': 150}
	star_class_AeBe = {'red': 202, 'green': 215, 'blue': 255, 'brightness': 105, 'saturation': 150}
	# Neutron Star
	star_class_N = {'red': 155, 'green': 176, 'blue': 255, 'brightness': 254, 'saturation': 254}
	star_class_H = {'red': 1, 'green': 1, 'blue': 1, 'brightness': 0, 'saturation': 0}
	star_class_SupermassiveBlackHole = {'red': 255, 'green': 255, 'blue': 255, 'brightness': 20, 'saturation': 5}
	star_class_M_RedSuperGiant = {'red': 255, 'green': 204, 'blue': 111, 'brightness': 254, 'saturation': 254}

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
	else:
		red = 255
		green = 255
		blue = 255
		bri = 0.8
		sat = 0
	bri = (bri / 254)
	return red, green, blue, bri, sat
