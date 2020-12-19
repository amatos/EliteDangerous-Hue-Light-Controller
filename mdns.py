import logging
import logging.config
import yaml

from time import sleep
from typing import cast

from zeroconf import IPVersion, ServiceBrowser, ServiceStateChange, Zeroconf, ZeroconfServiceTypes


class zeroconf_response:
    def __init__(self):
        self.host = ''
        self.ip = ''
        self.name = ''
        self.type = ''

    def populate(self, host, ip, name, type):
        self.host = host
        self.ip = ip
        self.name = name
        self.type = type


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



def mdns_search():
    def on_service_state_change(
            zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
    ) -> None:
        logger = logging.getLogger('EDHue.mDNS.handler')
        logger.debug("Service %s of type %s state changed: %s" % (name, service_type, state_change))

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            logger.debug("Info from zeroconf.get_service_info: %r" % (info))
            if info:
                addresses = ["%s:%d" % (addr, cast(int, info.port)) for addr in info.parsed_addresses()]
                logger.debug("  Addresses: %s" % ", ".join(addresses))
                logger.debug("  Weight: %d, priority: %d" % (info.weight, info.priority))
                logger.debug("  Server: %s" % (info.server,))
                zc_response.populate(host = info.server, ip = info.parsed_addresses(), name = info.name, type = info.type)
                if info.properties:
                    logger.debug("  Properties are:")
                    for key, value in info.properties.items():
                        logger.debug("    %s: %s" % (key, value))
                else:
                    logger.debug("  No properties")
            else:
                logger.debug("  No info")

    configure_logger()
    # create logger with 'EDHue'
    logger = logging.getLogger('EDHue.mDNS')
    zc_response = zeroconf_response()

    logger.debug('In mDNS search')
    zeroconf = Zeroconf()

    services = ["_hue._tcp.local."]

    logger.debug('Browsing for ' + str(services[0]))
    browser = ServiceBrowser(zeroconf, services, handlers=[on_service_state_change])

    sleep(3)
    logger.debug('Addresses returned: ' + str(zc_response.ip[0]))
    # addresses = on_service_state_change(zeroconf, services, )
    zeroconf.close()
    return zc_response.ip[0], zc_response.host, zc_response.name, zc_response.type

if __name__ == '__main__':
    mdns_search()