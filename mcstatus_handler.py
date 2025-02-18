from time import time, sleep
from mcstatus import JavaServer
from constants import RETRY_COUNT, RETRY_DELAY, LOG_FOLDER
import log

class Server:
    def __init__(self, server_ip):
        self.ip = server_ip
        self.server, self.timestamp, self.status = None, None, None
        self.update()

    @property # can be accessed like an attribute
    def players(self):
        return self.status.players

    @property
    def icon(self):
        return self.status.icon

    @property
    def modt(self):
        return (self.status.motd.parsed)

    def tracking_point(self):
        if self.update():
            return self.ip, self.timestamp, self.status.latency, self.status.players.online
        return False

    def update(self):
        tries = 1
        #print("Update") # Debug
        while tries <= RETRY_COUNT:
            try:
                self.server = JavaServer.lookup(self.ip)
                self.timestamp = int(time())
                self.status = self.server.status()
            except:
                log.warning("Server - update() - Server IP(" + str(self.ip) + ") update failed, retry " + str(tries) + " out of " + str(RETRY_COUNT))
            else:
                return True

            sleep(RETRY_DELAY)
            tries += 1
        log.error("Server - update() - Server IP(" + str(self.ip) + ") could not be updated")
        return False