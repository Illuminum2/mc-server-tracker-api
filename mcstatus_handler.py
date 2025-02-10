from mcstatus import JavaServer

class server:
    def __init__(self, server_ip):
        self.server = JavaServer.lookup(server_ip)
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