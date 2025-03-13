import asyncio
from time import time
import heapq

from src.db_handler import DBHandler
from src.mcstatus_handler import Server
from src.log import Logger as Log


class TrackingPointUpdater:
    def __init__(self, update_frequency, tracking_retention_time, server_retention_time, deleted_store_max):
        self.log = Log()

        self.db = DBHandler()

        self.update_frequency = update_frequency
        self.tracking_retention_time = tracking_retention_time
        self.server_retention_time = server_retention_time
        self._stop = False  # _ indicates variable is only to be used inside this class
        self.deleted_store_max = deleted_store_max

        self.servers = []
        self.current_index = 0
        self.last_list_update = 0
        self.deleted = 0
        self.deleted_indices = []

    def initialize_list(self):
        db_index = 0
        db_indices = self.db.servers.ids_all()
        self.last_list_update = int(time())
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

        if len(self.deleted_indices) is not 0:
            index = self.deleted_indices.pop(0)
        elif self.deleted > 0:
            await self.populate_deleted_indices()
            index = self.deleted_indices.pop(0)
        else:
            index = self.current_index

            self.current_index += 1
            if self.current_index >= self.update_frequency:
                self.current_index = 0

        self.servers[index].append([server, tracking_point_count])

    async def update_servers(self):
        servers = self.db.servers.ips_all_new(self.last_list_update)
        self.last_list_update = int(time())

        if not len(servers) == len(self.servers):
            old_servers = []
            for server_group in self.servers: # Get all current servers
                for server in server_group:
                    old_servers.append(server[0].ip)

            for server in servers:
                if server not in old_servers:
                    await self.add_server(server)

    async def clean(self):
        deleted_servers = self.db.servers.clean(self.server_retention_time)

        for i, server_group in enumerate(self.servers):
            for server in server_group:
                if server[0].ip in deleted_servers:
                    server_group.remove(server)
                    if len(self.deleted_indices) < self.deleted_store_max:
                        self.deleted_indices.append(i)
                    else:
                        self.deleted_indices.remove(0) # Or pop(-1)?
                        self.deleted_indices.append(i)
                    self.deleted += 1

    async def populate_deleted_indices(self):
        groups_count = []

        for i, server_group in enumerate(self.servers):
            groups_count.append((len(server_group), i))

        if self.update_frequency >= 150: # threshold for where heapsort is faster
            # Heapsort
            smallest_groups = heapq.nsmallest(min(self.deleted_store_max, self.deleted), groups_count)
        else:
            # Quicksort
            smallest_groups = sorted(groups_count)[:min(self.deleted_store_max, self.deleted)]
        self.deleted_indices = [group[1] for group in smallest_groups] # Populate with second element of tuple


    async def start(self):
        self._stop = False

        self.db.tracking_points.clean(self.tracking_retention_time)
        self.initialize_list() # Must be called after cleaning as tracking_point_count can change

        while not self._stop:
            self.log.info("TrackingPointsUpdater - start() - New round started")

            round_start_time = time()

            updates = []
            for i in range(self.update_frequency): # Loops and increments i as long as i < self.update_frequency
                updates.append(asyncio.create_task(self.update(self.servers[i])))
                sleep_time = (round_start_time + i+1) - time() # Dynamic wait time
                await asyncio.sleep(max(0.0, sleep_time))
            await asyncio.gather(*updates) # * unrolls the list
            await self.clean()
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