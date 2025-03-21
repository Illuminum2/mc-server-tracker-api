import os

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 8000))

API_ROOT_PATH = "/api"
MC_PORT = 25565

UPDATE_FREQUENCY = 60*5 # 5 min
TRACKING_RETENTION_TIME = 60*60*24*7 # 1 week
SERVER_RETENTION_TIME = 60*60*24*14 # 14 days

PROJECT_FOLDER = os.path.abspath("../")

DB_FOLDER = os.path.join(PROJECT_FOLDER, "db")
DB_FILE_NAME = "mc_tracker.db"
DB_PATH = os.path.join(DB_FOLDER, DB_FILE_NAME) # Uses correct path separator

LOG_FOLDER = os.path.join(PROJECT_FOLDER, "logs")
LOG_FILE_EXTENSION = ".log"

RETRY_COUNT = 3
RETRY_DELAY = 2

REQUEST_TIMEOUT = 5

DELETED_STORE_MAX = 10