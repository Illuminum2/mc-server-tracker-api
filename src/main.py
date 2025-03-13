import uvicorn
import asyncio

from src.db_handler import DBHandler
from src.tracking_point_updater import TrackingPointUpdater
from src.api import app
from src.constants import HOST, PORT, UPDATE_FREQUENCY, TRACKING_RETENTION_TIME, SERVER_RETENTION_TIME, DELETED_STORE_MAX, MC_PORT
from src.log import Logger as Log

async def main():
    log = Log()
    log.info("main() - MC Tracking API started")

    db = DBHandler()
    example_ip = f"mc.hypixel.net:{MC_PORT}"
    if not db.servers.exists_ip(example_ip):
        db.servers.add(example_ip, 0, 1)  # A permanent example

    restart = True

    while restart is True:
        config = uvicorn.Config(app=app, host=HOST, port=PORT, log_level="info")
        server = uvicorn.Server(config)
        try:
            await start(server)
        #except KeyboardInterrupt: # When stop is pressed
        #    print("Keyboard Interrupt")
        #    log.info("main() - Shutdown started")
        #    updater.stop() # Doesn't do anything
        #    restart = False
        except Exception as e:
            server.force_exit()
            log.error(f"main() - Error: {str(e)}")
            log.info(f"main() - Restart in progress")

    log.info("main() - Shutdown complete")

async def start(server):
    updater = TrackingPointUpdater(UPDATE_FREQUENCY, TRACKING_RETENTION_TIME, SERVER_RETENTION_TIME, DELETED_STORE_MAX)
    await asyncio.gather(updater.start(), start_api(server))

async def start_api(server):
    #uvicorn.run(app, host=HOST, port=PORT) # Not used because it is blocking
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())