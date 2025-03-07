import sqlite3
import os
from time import time
from log import Logger as Log
from constants import DB_FOLDER, DB_PATH

class DBConnection:
    def __init__(self):
        if not os.path.exists(DB_FOLDER):
            os.makedirs(DB_FOLDER)
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_ip TEXT NOT NULL,
                priv INTEGER NOT NULL,
                permanent INTEGER NOT NULL,
                last_update INTEGER,
                last_access INTEGER NOT NULL,
                access_count INTEGER,
                UNIQUE(server_ip)
            );
        """)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS tracking_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                timestamp INTEGER NOT NULL,
                latency INTEGER,
                players INTEGER,
                FOREIGN KEY (server_id) REFERENCES servers(id)  -- Foreign key(server_id) linking to id of servers table
            );
        """)
        self.connection.commit()

class DBServers:
    def __init__(self, connection, cursor, tracking_points):
        self.log = Log()

        self.conn = connection
        self.cursor = cursor
        self.tracking_points = tracking_points

    def exists_ip(self, server_ip):
        return bool(self.cursor.execute("SELECT * FROM servers WHERE server_ip = ?", [server_ip]).fetchall()) # If list is empty bool() returns False

    def exists_id(self, server_id):
        return bool(self.cursor.execute("SELECT * FROM servers WHERE id = ?", [server_id]).fetchall())

    def get_ip(self, server_id):
        if self.exists_id(server_id):
            return self.cursor.execute("SELECT * FROM servers WHERE id = ?", [server_id]).fetchone()[1]
        self.log.info(f"DBServers - get_ip() - Server ID({str(server_id)}) not found")
        return None

    def get_id(self, server_ip):
        if self.exists_ip(server_ip):
            return self.get(server_ip)[0]
        self.log.info(f"DBServers - get_id() - Server IP({str(server_ip)}) not found")
        return None

    def add(self, server_ip, private, permanent):
        if not self.exists_ip(server_ip):
            server = [server_ip, private, permanent, int(time()), 1]
            self.cursor.execute("INSERT INTO servers (server_ip, priv, permanent, last_access, access_count) VALUES (?, ?, ?, ?, ?)", server)
            self.conn.commit()
        else:
            self.log.info(f"DBServers - add() - Server IP({str(server_ip)}) already exists")

    def get(self, server_ip):
        if self.exists_ip(server_ip):
            server = self.cursor.execute("SELECT * FROM servers WHERE server_ip = ?", [server_ip]).fetchone()
            return server
        self.log.info(f"DBServers - get() - Server IP({str(server_ip)}) does not exist")
        return None

    @property
    def count_all(self): # Returns amount of servers
        return self.cursor.execute("SELECT count(id) FROM servers").fetchone()[0] # Indexing id would improve speed

    @property
    def count_public(self):  # Returns amount of servers
        return self.cursor.execute("SELECT count(id) FROM servers WHERE priv = 0").fetchone()[0]

    def ids_all(self):
        return [int(tuple_id[0]) for tuple_id in self.cursor.execute("SELECT id FROM servers").fetchall()]

    def ids_public(self):
        return [int(tuple_id[0]) for tuple_id in self.cursor.execute("SELECT id FROM servers WHERE priv = 0").fetchall()]

    def ips_public(self):
        return [str(tuple_ip[0]) for tuple_ip in self.cursor.execute("SELECT server_ip FROM servers WHERE priv = 0").fetchall()]

    def get_settings(self, server_ip):
        if self.exists_ip(server_ip):
            server = self.get(server_ip)
            priv, permanent = bool(server[2]), bool(server[3]) # Better readability
            return [priv, permanent]
        self.log.info(f"DBServers - get_settings() - Server IP({str(server_ip)}) does not exist")
        return None

    def get_status(self, server_ip):
        if self.exists_ip(server_ip):
            server = self.get(server_ip)
            last_update, last_access = server[4], server[5]
            return [last_update, last_access]
        self.log.info(f"DBServers - get_status() - Server IP({str(server_ip)}) does not exist")
        return None

    def get_access_count(self, server_ip):
        if self.exists_ip(server_ip):
            server = self.get(server_ip)
            access_count = server[6]
            return access_count # No list just a var
        self.log.info(f"DBServers - get_access_count() - Server IP({str(server_ip)}) does not exist")
        return None

    def update_last_update(self, server_ip, timestamp):
        if self.exists_ip(server_ip):
            self.cursor.execute("UPDATE servers SET last_update = ? WHERE server_ip = ?", [timestamp, server_ip])
            self.conn.commit()
            return
        self.log.info(f"DBServers - update_last_update() - Server IP({str(server_ip)}) does not exist")

    def update_access(self, server_ip, timestamp):
        if self.exists_ip(server_ip):
            self.cursor.execute("UPDATE servers SET access_count = access_count + 1 WHERE server_ip = ?", [server_ip])
            self.cursor.execute("UPDATE servers SET last_access = ? WHERE server_ip = ?", [timestamp, server_ip])
            self.conn.commit()
            return
        self.log.info(f"DBServers - update_access() - Server IP({str(server_ip)}) does not exist")

    def clean(self, retention_time):
        self.cursor.execute("DELETE FROM servers WHERE last_access < ? AND permanent = 0", [int(time()) - retention_time])
        self.conn.commit()

class DBTrackingPoints:
    def __init__(self, connection, cursor, servers):
        self.log = Log()

        self.conn = connection
        self.cursor = cursor
        self.servers = servers

    def add(self, tracking_point):
        server_ip = tracking_point[0]
        if self.servers.exists_ip(server_ip):
            timestamp = tracking_point[1]
            latency = tracking_point[2]
            players = tracking_point[3]
            server = [self.servers.get_id(server_ip), timestamp, latency, players]
            self.cursor.execute("INSERT INTO tracking_points (server_id, timestamp, latency, players) VALUES (?, ?, ?, ?)", server)
            self.conn.commit()
        else:
            self.log.info(f"DBTrackingPoints - add() - Server IP({str(server_ip)}) does not exist")

    def get(self, server_ip):
        if self.servers.exists_ip(server_ip):
            server_id = self.servers.get_id(server_ip)
            tracking_points = self.cursor.execute("SELECT server_id, timestamp, latency, players FROM tracking_points WHERE server_id = ?", [server_id])
            tracking_point = tracking_points.fetchone()
            results = []
            while tracking_point: # repeats until tracking_point is empty
                results.append(tracking_point)
                tracking_point = tracking_points.fetchone()
            return results
        self.log.info(f"DBTrackingPoints - get() - Server IP({str(server_ip)}) does not exist")
        return None

    def count(self, server_ip):
        if self.servers.exists_ip(server_ip):
            server_id = self.servers.get_id(server_ip)
            tracking_point_count = self.cursor.execute("SELECT count(server_id) FROM tracking_points WHERE server_id = ?", [server_id]).fetchone()[0]
            return tracking_point_count
        self.log.info(f"DBTrackingPoints - count() - Server IP({str(server_ip)}) does not exist")
        return None

    def clean(self, retention_time):
        self.cursor.execute("DELETE FROM tracking_points WHERE timestamp < ?", [int(time()) - retention_time])
        self.conn.commit()

    def delete_oldest(self, server_ip):
        if self.servers.exists_ip(server_ip):
            self.cursor.execute("DELETE FROM tracking_points WHERE id ="
                                "(SELECT id FROM tracking_points WHERE server_id = ? ORDER BY timestamp LIMIT 1)", [self.servers.get_id(server_ip)]) # Using a subquery
            self.conn.commit()
        else:
            self.log.info(f"DBTrackingPoints - delete_oldest() - Server IP({str(server_ip)}) does not exist")

class Singleton(type): # https://stackoverflow.com/questions/6760685/
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DBHandler(metaclass=Singleton):
    def __init__(self):
        self.conn = DBConnection().connection
        self.cursor = self.conn.cursor()
        self.servers = DBServers(self.conn, self.cursor, None)
        self.tracking_points = DBTrackingPoints(self.conn, self.cursor, self.servers)
        self.servers.tracking_points = self.tracking_points
        
        self.log = Log()
        self.log.info("DBHandler - init() - Connected DBServers and DBTrackingPoints with database")