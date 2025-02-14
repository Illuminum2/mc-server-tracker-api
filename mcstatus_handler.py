from time import time
from mcstatus import JavaServer
#from websockets.sync.server import serve


class Server:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.server = JavaServer.lookup(self.server_ip)
        self.timestamp = int(time())
        self.status = self.server.status()

    @property # can be accessed like an attribute
    def players(self):
        return self.status.players

    @property
    def icon(self):
        return self.status.icon

    @property
    def modt(self):
        return (self.status.motd.parsed)

    @property
    def tracking_point(self):
        return self.server_ip, self.timestamp, self.status.latency, self.status.players.online

    def update(self):
        self.server = JavaServer.lookup(self.server_ip)
        self.status = self.server.status()
        self.timestamp = int(time())

