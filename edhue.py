import logging
import logging.config
import time
import os

import yaml

from SavedGamesLocator import get_saved_games_path
from hue_light import HueLightControl
from journal import JournalWatcher, JournalChangeProcessor
from stars import star_color

default_journal_path = get_saved_games_path()


class EDHue:
	def __init__(
			self,
			hue_light='',
			force_polling=False,
			journal_watcher=None,
			journal_change_processor=JournalChangeProcessor()):

		configure_logger()
		self.logger = logging.getLogger('EDHue.ED_Hue')
		self.logger.debug('Initializing EDHue class.')
		if hue_light != '':
			self.hue_light = hue_light
			self.hue = HueLightControl(self.hue_light)
		if journal_watcher is None:
			journal_watcher = JournalWatcher(default_journal_path, force_polling=force_polling)

		# Setup the journal watcher
		self.logger.debug('Set up the journal watcher.')
		self.journal_change_processor = journal_change_processor
		self.journalWatcher = journal_watcher
		self.journalWatcher.set_callback(self.on_journal_change)

	def trigger_current_journal_check(self):
		self.logger.debug('In trigger_current_journal_check.')
		self.journalWatcher.trigger_current_journal_check()

	def process_journal_change(self, new_entry):
		self.logger.debug('In process_journal_change.')
		self.logger.debug('New event:')
		self.logger.debug('  ' + str(new_entry))
		self.logger.info('Received ' + new_entry['event'] + ' event.')
		# Control lights
		if new_entry['event'] == 'StartJump':
			self.logger.debug('Received a StartJump event.')
			self.logger.debug('Setting a color loop.')
			self.hue.colorloop()
			if new_entry['JumpType'] == 'Hyperspace':
				self.logger.debug('Jump type is Hyperspace!')
				self.logger.debug('Found a star ' + new_entry['StarClass'])
				r, g, b, bright, sat = star_color(new_entry['StarClass'])
				self.logger.debug('Star RGB: ' + str(r) + ' ' + str(g) + ' ' + str(b))
				self.hue.set_star(r=r, g=g, b=b, bright=bright)
		if new_entry['event'] == 'FSDJump':
			self.logger.debug('Received an FSDJump event.')
			self.logger.debug('Clearing color loop')
			self.hue.clear_colorloop()
			self.logger.debug('Colorizing light')
			self.hue.starlight()

	def on_journal_change(self, altered_journal):
		self.logger.debug('In on_journal_change.')
		entries = self.journal_change_processor.process_journal_change(altered_journal)
		number_entries = len(entries)
		self.logger.debug('Processing ' + str(number_entries) + ' entries.')
		for new_entry in entries:
			self.process_journal_change(new_entry)

	def stop(self):
		self.logger.debug('Stopping journal watcher.')
		self.journalWatcher.stop()


def configure_logger(debug=False):
	"""Load settings from logging.yaml

	@return:
	"""
	# Load logging config
	with open('logging.yaml', 'r') as f:
		log_cfg = yaml.safe_load(f.read())
	if debug:
		for log_type in log_cfg['loggers']:
			log_cfg['loggers'][log_type]['handlers'] = ['console', 'file']
	logging.config.dictConfig(log_cfg)
	return


def initialize():
	if os.path.exists('config.py'):
		import config
		hue_IP = config.hue_IP
		hue_light = config.hue_light
		debug = config.debug
	else:
		hue_IP = ''
		hue_light = ''
		debug = False
	return hue_IP, hue_light, debug


def main():
	hue_IP, hue_light, debug = initialize()
	configure_logger(debug)
	# create logger with 'EDHue'
	logger = logging.getLogger('EDHue')

	logger.info('Starting.')
	if debug:
		logger.debug('Debugging mode enabled.')
	hue = HueLightControl(hue_light)
	ed_hue = EDHue(hue_light)

	logger.info('ED Hue is active.  Awaiting events...')
	hue.light_on()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		logger.info('Interrupt received.  Shutting down.')
		hue.light_off()
		ed_hue.stop()


if __name__ == '__main__':
	main()
