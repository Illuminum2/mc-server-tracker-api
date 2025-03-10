import logging

import os
from time import time

from src.constants import LOG_FOLDER, LOG_FILE_EXTENSION

class Singleton(type): # https://stackoverflow.com/questions/6760685/
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=Singleton):
    def __init__(self):
        if not os.path.exists(LOG_FOLDER):
            os.makedirs(LOG_FOLDER)
        self.log_path = os.path.join(LOG_FOLDER, str(int(time())) + LOG_FILE_EXTENSION)
        logging.basicConfig(filename=self.log_path, level=logging.INFO)
        self.log = logging.getLogger()

    def info(self, message):
        self.log.info(str(int(time())) + " - Info - " + message)

    def warning(self, message):
        self.log.warning(str(int(time())) + " - Warning - " + message)

    def error(self, message):
        self.log.error(str(int(time())) + " - Error - " + message)

    def clear(self):
        open(self.log_path, 'w').close()