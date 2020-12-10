import configparser
import logging


logger = logging.getLogger('experiment_logger')


def get_conf(path='config.ini'):
    conf = configparser.ConfigParser()
    conf.read(path)
    return conf


def show_conf(conf):
    for section in conf.sections():
        logger.info(section)
        for item in conf.items(section=section):
            logger.info(item)