import asyncio
import uvicorn
from tracking_point_updater import TrackingPointUpdater
from constants import HOST, PORT, UPDATE_FREQUENCY, TRACKING_RETENTION_TIME, SERVER_RETENTION_TIME
from api import app
from log import Logger as Log
from db_handler import DBHandler

async def start_api():
    #uvicorn.run(app, host=HOST, port=PORT) # Not used because it is blocking
    config = uvicorn.Config(app=app, host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    log = Log()
    log.info("main() - MC Tracking API started")

    db = DBHandler()
    if not db.servers.exists_ip("mc.hypixel.net:25565"):
        db.servers.add("mc.hypixel.net:25565", 0, 1)  # A permanent example

    updater = TrackingPointUpdater(UPDATE_FREQUENCY, TRACKING_RETENTION_TIME, SERVER_RETENTION_TIME)

    try:
        await asyncio.gather(updater.start(), start_api())
    #except KeyboardInterrupt: # When stop is pressed
    #    log.info("main() - Shutdown started")
    #    updater.stop()
    except Exception as e:
        log.error(f"main() - Error: {str(e)}")

    log.info("main() - Shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())