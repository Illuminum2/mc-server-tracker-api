import asyncio
import uvicorn

from tracking_point_updater import TrackingPointUpdater
from constants import HOST, PORT, UPDATE_FREQUENCY, TRACKING_RETENTION_TIME, SERVER_RETENTION_TIME, MC_PORT
from api import app
from log import Logger as Log
from db_handler import DBHandler

async def main():
    log = Log()
    log.info("main() - MC Tracking API started")

    db = DBHandler()
    example_ip = f"mc.hypixel.net:{MC_PORT}"
    if not db.servers.exists_ip(example_ip):
        db.servers.add(example_ip, 0, 1)  # A permanent example

    restart = True

    while restart is True:
        try:
            await start()
        #except KeyboardInterrupt: # When stop is pressed
        #    log.info("main() - Shutdown started")
        #    updater.stop()
        #    restart = False
        except Exception as e:
            log.error(f"main() - Error: {str(e)}")
            log.info(f"main() - Restart in progress")

    log.info("main() - Shutdown complete")

async def start():
    updater = TrackingPointUpdater(UPDATE_FREQUENCY, TRACKING_RETENTION_TIME, SERVER_RETENTION_TIME)
    await asyncio.gather(updater.start(), start_api())

async def start_api():
    #uvicorn.run(app, host=HOST, port=PORT) # Not used because it is blocking
    config = uvicorn.Config(app=app, host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())