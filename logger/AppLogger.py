import logging
from datetime import datetime

# TODO Change these when I come up with an app name
APP_LOGGER_NAME = "App"
APP_LOG_FILENAME = 'app.log'

def build_logger(logger_name = APP_LOGGER_NAME, filename = APP_LOG_FILENAME, debug = False):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    fileHandler = logging.FileHandler(filename)

    consoleHandler.setLevel(logging.DEBUG if debug else logging.INFO)
    fileHandler.setLevel(logging.WARNING)

    formatter = logging.Formatter('[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s', datefmt="%m/%d/%y %H:%M:%S")

    consoleHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

    return logger