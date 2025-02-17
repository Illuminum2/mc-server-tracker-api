from db_handler import DBHandler
from mcstatus_handler import Server
from time import time, sleep

class TrackingPointUpdater():
    def __init__(self, db_path, update_frequency, retention_time):
        self.db = DBHandler(db_path)
        self.update_frequency = update_frequency
        self.retention_time = retention_time
        self.servers = []
        self.initializeList()
        self._stop = False # _ indicates variable is only to be used inside this class

    def initializeList(self):
        db_index = 0
        db_indices = self.db.servers.ids()
        db_len = len(db_indices)

        for i in range(self.update_frequency):
            self.servers.append([])

        while db_index < db_len:
            i = 0
            while i < self.update_frequency and db_index < db_len:
                print("Server IP: " + self.db.servers.get_ip(db_indices[db_index]))
                server = Server(self.db.servers.get_ip(db_indices[db_index]))
                tracking_point_count = self.db.tracking_points.count(server.ip)
                self.servers[i].append([server, tracking_point_count])
                i += 1
                db_index += 1

    def start(self):
        self.db.tracking_points.clean(self.retention_time)

        while not self._stop:
            print("New round")
            round_start_time = time()
            for i in range(self.update_frequency): # Loops and increments i as long as i < self.update_frequency
                self.update(self.servers[i])
                sleep_time = (round_start_time + i+1) - time() # Dynamic wait time
                sleep(max(0, sleep_time))

    def update(self, server_list):
        for server in server_list:
            self.db.tracking_points.add(server[0].tracking_point())
            if server[1] >= int(self.retention_time / self.update_frequency):
                self.db.tracking_points.delete_oldest(server[0].ip)
                #print(server.tracking_point()) # Debug

    def stop(self):
        self._stop = True