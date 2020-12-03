import configparser
import logging


logger = logging.getLogger('experiment_logger')


def get_conf():
    conf = configparser.ConfigParser()
    conf.read('config.ini')
    return conf


def show_conf(conf):
    for section in conf.sections():
        logger.info(section)
        for item in conf.items(section=section):
            logger.info(item)