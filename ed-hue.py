import logging
import time
from SavedGamesLocator import get_saved_games_path
from hue_light import hue_light_control
from journal import JournalWatcher, JournalChangeProcessor
from stars import star_color

default_journal_path = get_saved_games_path()

class ED_hue():
    def __init__(
            self,
            force_polling=False,
            journal_watcher=None,
            journal_change_processor=JournalChangeProcessor()):

        if journal_watcher is None:
            journal_watcher = JournalWatcher(default_journal_path, force_polling=force_polling)

        # Setup the journal watcher
        self.journal_change_processor = journal_change_processor
        self.journalWatcher = journal_watcher
        self.journalWatcher.set_callback(self.on_journal_change)

    def trigger_current_journal_check(self):
        self.journalWatcher.trigger_current_journal_check()

    def process_journal_change(self, new_entry):
        # Some stuff we don't care about
        excluded_event_types = ["Music", "ReceiveText"]
        if new_entry["event"] in excluded_event_types:
            return
        # Control lights
        logger.debug(new_entry)
        if new_entry['event'] == 'StartJump':
            logger.debug('Setting a color loop.')
            hue.colorloop()
            if new_entry['JumpType'] == 'Hyperspace':
                logger.debug('Found a star ' + new_entry['StarClass'])
                r, g, b, bright, sat = star_color(new_entry['StarClass'])
                logger.debug('Star RGB: ' + str(r) + ' ' + str(g) + ' ' + str(b))
                hue.set_star(r=r, g=g, b=b, bright=bright)
        if  new_entry['event'] == 'FSDJump':
            hue.clear_colorloop()
            logger.debug('Colorizing light')
            hue.starlight()
        else:
            pass

    def on_journal_change(self, altered_journal):
        entries = self.journal_change_processor.process_journal_change(altered_journal)
        self.process_new_journal_entries(entries)

    def process_new_journal_entries(self, entries):
        for new_entry in entries:
            self.process_journal_change(new_entry)

    def stop(self):
        self.journalWatcher.stop()

if __name__ == '__main__':
    # create logger with 'EDHue'
    logger = logging.getLogger('EDHue')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('edhue.log')
    fh.setLevel(logging.DEBUG)
    
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info('Starting.')
    ed_hue = ED_hue()
    hue = hue_light_control()

    logger.info('ED Hue is active.  Waiting events...')
    hue.light_on()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('done')
        hue.light_off()

    ed_hue.stop()