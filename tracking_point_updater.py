from db_handler import DBHandler
from mcstatus_handler import Server
from time import time, sleep

class TrackingPointUpdater():
    def __init__(self, db_path, update_frequency):
        self.db = DBHandler(db_path)
        self.update_frequency = update_frequency
        self.servers = []
        self.initializeList()

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
                self.servers[i].append(Server(self.db.servers.get_ip(db_indices[db_index])))
                i += 1
                db_index += 1

    def start(self):
        while True:
            round_start_time = time()
            for i in range(self.update_frequency): # Loops and increments i as long as i < self.update_frequency
                self.update(self.servers[i])
                sleep_time = (round_start_time + i+1) - time() # Dynamic wait time
                sleep(max(0, sleep_time))

    def update(self, server_list):
        for server in server_list:
            self.db.tracking_points.add(server.tracking_point())
            self.db.tracking_points.delete_oldest(server.ip)
            #print(server.tracking_point()) # Debug