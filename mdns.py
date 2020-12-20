import logging
import logging.config
from time import sleep
from typing import cast

import yaml
from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf


class zeroConfResponse:
    def __init__(self):
        self.host = ''
        self.ip = ''
        self.name = ''
        self.type = ''
        self.populated = False

    def populate(self, host, ip, name, mdns_type):
        self.host = host
        self.ip = ip
        self.name = name
        self.type = mdns_type
        self.populated = True


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
        logger.debug("Service %s of mdns_type %s state changed: %s" % (name, service_type, state_change))

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            logger.debug("Info from zc.get_service_info: %r" % info)
            if info:
                addresses = ["%s:%d" % (address, cast(int, info.port)) for address in info.parsed_addresses()]
                logger.debug("  Addresses: %s" % ", ".join(addresses))
                logger.debug("  Weight: %d, priority: %d" % (info.weight, info.priority))
                logger.debug("  Server: %s" % (info.server,))
                zc_response.populate(host=info.server, ip=info.parsed_addresses(), name=info.name, mdns_type=info.type)
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
    zc_response = zeroConfResponse()

    logger.debug('In mDNS search')
    zc = Zeroconf()
    ip = ''
    hostname = ''
    name = ''
    mdns_type = ''
    services = ["_hue._tcp.local."]

    logger.debug('Browsing for ' + str(services[0]))
    browser = ServiceBrowser(zc, services, handlers=[on_service_state_change])

    logger.debug('Waiting up to 5 seconds for mDNS response.')
    for counter in range(50):
        if zc_response.populated:
            logger.debug('Found a Philips Hue bridge.  Proceeding.')
            ip = zc_response.ip[0]
            hostname = zc_response.host
            name = zc_response.name
            mdns_type = zc_response.type
            break
        sleep(.1)
        logger.debug('Still searching.')
    zc.close()
    if ip != '':
        logger.debug('Addresses returned: ' + ip)
    else:
        logger.debug('Bridge not found within 5 seconds.')
    return ip, hostname, name, mdns_type


if __name__ == '__main__':
    mdns_search()
