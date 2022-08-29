import logging
import os
import sys

APP_LOGGER_NAME = "Deskity"
APP_LOG_FILENAME = "deskity.log"

LEVEL_NAME_FORMAT_PART = '%(levelname)-7s'
NAME_FORMAT_PART = '%(name)-12s'
TIME_FORMAT_PART = '%(asctime)s'
MESSAGE_FORMAT_PART = '%(message)s'
FILENAME_FORMAT_PART = '%(filename)s'
LINE_NUMBER_FORMAT_PART = '%(lineno)d'

class ColorFormatter(logging.Formatter):
    cyan_bold = "\x1b[36;1m"
    green_bold = "\x1b[32;1m"
    yellow = "\x1b[33;20m"
    yellow_bold = "\x1b[33;1m"
    red_bold = "\x1b[31;1m"
    reset = "\x1b[0m"

    base_format = f"[{NAME_FORMAT_PART}] {MESSAGE_FORMAT_PART}"

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, *,
                 defaults=None, use_logger_origin=True):
        if use_logger_origin:
            self.base_format = self.base_format + f' {self.yellow}({FILENAME_FORMAT_PART}:{LINE_NUMBER_FORMAT_PART}){self.reset}'

        self.FORMATS = {
            logging.DEBUG: f"[{self.cyan_bold}{LEVEL_NAME_FORMAT_PART}{self.reset}] {self.base_format}",
            logging.INFO: f"[{self.green_bold}{LEVEL_NAME_FORMAT_PART}{self.reset}] {self.base_format}",
            logging.WARNING: f"[{self.yellow_bold}{LEVEL_NAME_FORMAT_PART}{self.reset}] {self.base_format}",
            logging.ERROR: f"[{self.red_bold}{LEVEL_NAME_FORMAT_PART}{self.reset}] {self.base_format}",
            logging.CRITICAL: f"[{self.red_bold}{LEVEL_NAME_FORMAT_PART}{self.reset}] {self.base_format}"
        }

        super(ColorFormatter, self).__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults)

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

def build_logger(logger_name = APP_LOGGER_NAME, filename = APP_LOG_FILENAME, debug = False, use_logger_origin=True):
    """Build a new logger object, set up with all the proper settings for both console and file logging"""

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    log_path = os.path.normpath(f'{os.path.dirname(os.path.abspath(__file__))}/../..')
    fileHandler = logging.FileHandler(f"{log_path}/{filename}")

    consoleHandler.setLevel(logging.DEBUG if debug else logging.INFO)
    fileHandler.setLevel(logging.WARNING)

    date_format = "%m/%d/%y %H:%M:%S"
    base_format = f'[{LEVEL_NAME_FORMAT_PART}] [{NAME_FORMAT_PART}] [{TIME_FORMAT_PART}] {MESSAGE_FORMAT_PART}'
    if use_logger_origin:
        base_format = base_format + f' ({FILENAME_FORMAT_PART}:{LINE_NUMBER_FORMAT_PART})'
    consoleHandler.setFormatter(ColorFormatter(datefmt=date_format, use_logger_origin=use_logger_origin))
    fileHandler.setFormatter(logging.Formatter(base_format, datefmt=date_format))

    logger.handlers.clear()
    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

    return logger