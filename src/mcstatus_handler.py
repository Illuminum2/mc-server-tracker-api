from mcstatus import JavaServer

from time import time, sleep

from src.constants import RETRY_COUNT, RETRY_DELAY, REQUEST_TIMEOUT
from src.log import Logger as Log


class Server:
    def __init__(self, server_ip):
        self.log = Log()

        self.ip = server_ip
        self.server, self.timestamp, self.status, self.query = None, None, None, None
        self.update()

    @property
    def players(self):
        if self.status is None:
            self.log.error(f"Server - players() - Server IP({str(self.ip)}): No status data available")
            return None
        return self.status.players

    @property
    def version(self):
        if self.status is None:
            self.log.error(f"Server - version() - Server IP({str(self.ip)}): No status data available")
            return None
        return self.status.version

    @property
    def enforces_secure_chat(self):
        if self.status is None:
            self.log.error(f"Server - enforce_secure_chat() - Server IP({str(self.ip)}): No status data available")
            return None
        return self.status.enforces_secure_chat

    @property
    def latency(self):
        if self.status is None:
            self.log.error(f"Server - latency() - Server IP({str(self.ip)}): No status data available")
            return None
        return self.status.latency

    @property
    def modt(self):
        if self.status is None:
            self.log.error(f"Server - modt() - Server IP({str(self.ip)}): No status data available")
            return None
        return self.status.motd.to_minecraft()

    @property
    def icon(self):
        if self.status is None:
            self.log.error(f"Server - icon() - Server IP({str(self.ip)}): No status data available")
            return None
        return self.status.icon

    @property
    def software(self):
        self.update_query()
        if self.query is None:
            if self.status is not None:
                #self.log.error("Server - software() - Server IP(" + str(self.ip) + "): Querying is not enabled on the server")
                return None
            self.log.error(f"Server - software() - Server IP({str(self.ip)}): No query data available")
            return None
        return self.query.software()

    @property
    def map(self):
        self.update_query()
        if self.query is None:
            if self.status is not None:
                #self.log.error("Server - map() - Server IP(" + str(self.ip) + "): Querying is not enabled on the server")
                return None
            self.log.error(f"Server - map() - Server IP({str(self.ip)}): No query data available")
            return None
        return self.query.map

    def tracking_point(self):
        if self.update():
            return self.ip, self.timestamp, self.latency, self.players.online
        return False

    def update(self):
        tries = 1
        success = False
        while tries <= RETRY_COUNT and success is False:
            if tries >= 2:
                sleep(RETRY_DELAY)

            try:
                self.server = JavaServer.lookup(self.ip, REQUEST_TIMEOUT)
                self.timestamp = int(time())
                success = True
            except TimeoutError:
                self.log.warning(f"Server - update() - Server IP({self.ip}) lookup timeout, retry {tries} out of {RETRY_COUNT}")
            except ConnectionRefusedError:
                self.log.warning(f"Server - update() - Server IP({self.ip}) lookup connection refused, retry {tries} out of {RETRY_COUNT}")
            except Exception as e:
                self.log.warning(f"Server - update() - Server IP({self.ip}) lookup failed: {str(e)}, retry {tries} out of {RETRY_COUNT}")
            tries += 1

        if self.server is None:
            self.log.error(f"Server - update() - Server IP({self.ip}) could not be looked up")
            return False

        tries = 1
        success = False
        while tries <= RETRY_COUNT and success is False:
            if tries >= 2:
                sleep(RETRY_DELAY)
            try:
                self.status = self.server.status()
                success = True
            except TimeoutError:
                self.log.warning(f"Server - update() - Server IP({self.ip}) status timeout, retry {tries} out of {RETRY_COUNT}")
                self.status = None
            except ConnectionRefusedError:
                self.log.warning(f"Server - update() - Server IP({self.ip}) status connection refused, retry {tries} out of {RETRY_COUNT}")
                self.status = None
            except Exception as e:
                self.log.warning(f"Server - update() - Server IP({self.ip}) status failed: {str(e)}, retry {tries} out of {RETRY_COUNT}")
                self.status = None

            tries += 1

        if self.status is None:
            self.log.error(f"Server - update() - Server IP({self.ip}) status could not be retrieved")
            return False

        return True

    def update_query(self):
        if self.status is None:
            self.update()

        if self.query is None:
            try: # Fails on servers with query disabled
                self.query = self.server.query()
                # Query success is a bonus, not required
            except TimeoutError:
                self.log.info(f"Server - update() - Server IP({self.ip}) query timeout - query likely disabled")
                self.query = None
            except ConnectionRefusedError:
                self.log.info(f"Server - update() - Server IP({self.ip}) query connection refused - query likely disabled")
                self.query = None
            except Exception as e:
                self.log.info(f"Server - update() - Server IP({self.ip}) query failed: {str(e)}")
                self.query = None