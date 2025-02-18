from time import time
import logging
from constants import LOG_FOLDER, LOG_FILE_EXTENSION

log_path = LOG_FOLDER + str(int(time())) + LOG_FILE_EXTENSION
logging.basicConfig(filename=log_path, level=logging.INFO)
log = logging.getLogger()

def info(message):
    log.info(str(int(time())) + " - Info - " + message)

def warning(message):
    log.warning(str(int(time())) + " - Warning - " + message)

def error(message):
    log.error(str(int(time())) + " - Error - " + message)

def clear():
    open(log_path, 'w').close()