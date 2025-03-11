import asyncio
from time import time

from src.db_handler import DBHandler
from src.mcstatus_handler import Server
from src.log import Logger as Log

class TrackingPointUpdater():
    def __init__(self, update_frequency, tracking_retention_time, server_retention_time):
        self.log = Log()

        self.db = DBHandler()

        self.update_frequency = update_frequency
        self.tracking_retention_time = tracking_retention_time
        self.server_retention_time = server_retention_time
        self._stop = False  # _ indicates variable is only to be used inside this class

        self.servers = []
        self.current_index = 0

    def initializeList(self):
        db_index = 0
        db_indices = self.db.servers.ids_all()
        db_len = len(db_indices)

        for i in range(self.update_frequency):
            self.servers.append([])

        while db_index < db_len:
            self.current_index = 0
            while self.current_index < self.update_frequency and db_index < db_len:
                #print("Server IP: " + self.db.servers.get_ip(db_indices[db_index])) # Debug
                server = Server(self.db.servers.get_ip(db_indices[db_index]))
                tracking_point_count = self.db.count_tracking_points(server.ip)
                self.servers[self.current_index].append([server, tracking_point_count])
                self.current_index += 1
                db_index += 1

        self.log.info("TrackingPointsUpdater - initializeList() - List initialized")

    async def add_server(self, ip):
        server = Server(ip)
        tracking_point_count = self.db.count_tracking_points(server.ip) # Could technically be skipped as it is going to be 0
        self.servers[self.current_index].append([server, tracking_point_count])

        self.current_index += 1
        if self.current_index >= self.update_frequency:
            self.current_index = 0


    async def update_servers(self):
        servers = self.db.servers.ips_all()

        if not len(servers) == len(self.servers):
            old_servers = []
            for server_group in self.servers: # Get all current servers
                for server in server_group:
                    old_servers.append(server[0].ip)

            for server in servers:
                if server not in old_servers:
                    await self.add_server(server)

    async def start(self):
        self._stop = False

        self.db.tracking_points.clean(self.tracking_retention_time)
        self.initializeList() # Must be called after cleaning as tracking_point_count can change

        while not self._stop:
            self.log.info("TrackingPointsUpdater - start() - New round started")

            round_start_time = time()

            updates = []
            for i in range(self.update_frequency): # Loops and increments i as long as i < self.update_frequency
                updates.append(asyncio.create_task(self.update(self.servers[i])))
                sleep_time = (round_start_time + i+1) - time() # Dynamic wait time
                await asyncio.sleep(max(0, sleep_time))
            await asyncio.gather(*updates) # * unrolls the list
            self.db.servers.clean(self.server_retention_time)
            await self.update_servers()

    async def update(self, server_list):
        for server in server_list:
            tracking_point = server[0].tracking_point()
            if tracking_point:
                self.db.add_tracking_point(tracking_point)
                self.db.servers.update_last_update(tracking_point[0], tracking_point[1])
                server[1] += 1

            if server[1] > int(self.tracking_retention_time / self.update_frequency):
                self.db.delete_oldest_tracking_point(server[0].ip)
                server[1] -= 1

    def stop(self):
        self._stop = True
        self.log.info("TrackingPointsUpdater - stop() - TrackingPointUpdater() stop initiated")