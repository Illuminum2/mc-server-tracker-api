from db_handler import DBHandler
from mcstatus_handler import Server
from time import time, sleep
import log
import asyncio

class TrackingPointUpdater():
    def __init__(self, db_path, update_frequency, tracking_retention_time, server_retention_time):
        self.db = DBHandler(db_path)

        self.update_frequency = update_frequency
        self.tracking_retention_time = tracking_retention_time
        self.server_retention_time = server_retention_time
        self._stop = False  # _ indicates variable is only to be used inside this class

        self.servers = []

    def initializeList(self):
        db_index = 0
        db_indices = self.db.servers.ids_all()
        db_len = len(db_indices)

        for i in range(self.update_frequency):
            self.servers.append([])

        while db_index < db_len:
            i = 0
            while i < self.update_frequency and db_index < db_len:
                #print("Server IP: " + self.db.servers.get_ip(db_indices[db_index])) # Debug
                server = Server(self.db.servers.get_ip(db_indices[db_index]))
                tracking_point_count = self.db.tracking_points.count(server.ip)
                self.servers[i].append([server, tracking_point_count])
                i += 1
                db_index += 1

        log.info("TrackingPointsUpdater - initializeList() - List initialized")

    async def start(self):
        self._stop = False

        self.db.tracking_points.clean(self.tracking_retention_time)
        self.initializeList() # Must be called after cleaning as tracking_point_count can change

        while not self._stop:
            log.info("TrackingPointsUpdater - start() - New round started")

            round_start_time = time()

            updates = []
            for i in range(self.update_frequency): # Loops and increments i as long as i < self.update_frequency
                updates.append(asyncio.create_task(self.update(self.servers[i])))
                sleep_time = (round_start_time + i+1) - time() # Dynamic wait time
                sleep(max(0, sleep_time))
            await asyncio.gather(*updates) # * unrolls the list
            self.db.servers.clean(self.server_retention_time)

    async def update(self, server_list):
        for server in server_list:
            tracking_point = server[0].tracking_point()
            if tracking_point:
                self.db.tracking_points.add(tracking_point)
                self.db.servers.update_last_update(tracking_point[0], tracking_point[1])
                server[1] += 1

            if server[1] > int(self.tracking_retention_time / self.update_frequency):
                self.db.tracking_points.delete_oldest(server[0].ip)
                server[1] -= 1

    def stop(self):
        self._stop = True
        log.info("TrackingPointsUpdater - stop() - TrackingPointUpdater() stop initiated")