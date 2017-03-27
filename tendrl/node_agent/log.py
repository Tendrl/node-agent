import logging.config
import os

import yaml


class LogInitFailedError(Exception):
    def __init___(self, err):
        self.message = "Error: %s".format(err)


def setup_logging(
        log_cfg_path
):
    """Setup logging configuration

    """
    if os.path.exists(log_cfg_path):
        with open(log_cfg_path, 'rt') as f:
            log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
    else:
        raise LogInitFailedError("logging configuration not found at %s" %
                                 log_cfg_path)
