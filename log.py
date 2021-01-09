import yaml


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
    return log_cfg
