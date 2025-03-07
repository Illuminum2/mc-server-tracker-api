import os


UPDATE_FREQUENCY = 60*5 # 5 min
TRACKING_RETENTION_TIME = 60*60*24 # 24h
SERVER_RETENTION_TIME = 60*60*24*10 # 10 days

DB_FOLDER = "../db/"
DB_FILE_NAME = "mc_tracker.db"
DB_PATH = os.path.join(DB_FOLDER, DB_FILE_NAME) # Uses correct path separator

LOG_FOLDER = "../logs/"
LOG_FILE_EXTENSION = ".log"

RETRY_COUNT = 3
RETRY_DELAY = 2

REQUEST_TIMEOUT = 5