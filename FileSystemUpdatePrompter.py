import logging
import logging.config
import os
from threading import Thread
from time import sleep

import yaml

logger = logging.getLogger('EDHue.FileSystemUpdatePrompter')


class FileSystemUpdatePrompter:

	def __init__(self, path_to_query):
		# Load logging config
		with open('logging.yaml', 'r') as f:
			log_cfg = yaml.safe_load(f.read())
		logging.config.dictConfig(log_cfg)
		self.logger = logging.getLogger('EDHue.FileSystemUpdatePrompter')
		self.path_to_query = path_to_query
		self.file_size = None

		self.logger.debug('Starting filesystem watch daemon.')
		t = Thread(target=self.file_check)
		t.daemon = True
		t.start()

	def file_check(self):
		while True:
			new_size = os.stat(self.path_to_query).st_size

			if self.file_size is None:
				self.logger.debug(f"File size check: {new_size}")
			elif new_size != self.file_size:
				self.logger.debug(f"File size check: {new_size} (+{new_size - self.file_size})")

			self.file_size = new_size

			sleep(0.1)

	def set_watch_file(self, path_to_query):
		self.logger.debug('Looking for logs in: ' + path_to_query)
		self.path_to_query = path_to_query
