import logging
import os

APP_LOGGER_NAME = "Deskity"
APP_LOG_FILENAME = "deskity.log"

def build_logger(logger_name = APP_LOGGER_NAME, filename = APP_LOG_FILENAME, debug = False):
    """Build a new logger object, set up with all the proper settings for both console and file logging"""

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    log_path = os.path.normpath(f'{os.path.dirname(os.path.abspath(__file__))}/../..')
    fileHandler = logging.FileHandler(f"{log_path}/{filename}")

    consoleHandler.setLevel(logging.DEBUG if debug else logging.INFO)
    fileHandler.setLevel(logging.WARNING)

    formatter = logging.Formatter('[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s', datefmt="%m/%d/%y %H:%M:%S")

    consoleHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

    return logger