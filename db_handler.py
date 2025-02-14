import sqlite3
from time import time

class DBConnection:
    def __init__(self, servers_db_path):
        self.connection = sqlite3.connect(servers_db_path)
        self.cursor = self.connection.cursor()
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_ip TEXT NOT NULL,
                priv INTEGER NOT NULL,
                permanent INTEGER NOT NULL,
                last_update INTEGER,
                last_access INTEGER NOT NULL,
                access_count INTEGER
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

class DBHandler:
    def __init__(self, connection):
        self.servers = connection
        self.servers_c = self.servers.cursor()

    def exists_server_ip(self, server_ip):
        return bool(self.servers_c.execute("SELECT * FROM servers WHERE server_ip = ?", [server_ip]).fetchall()) # If list is empty bool() returns False

    def add_server(self, server_ip, private, permanent):
        if not self.exists_server_ip(server_ip):
            server = [server_ip, private, permanent, int(time()), 1]
            self.servers_c.execute("INSERT INTO servers (server_ip, priv, permanent, last_access, access_count) VALUES (?, ?, ?, ?, ?)", server)
            self.servers.commit()

    def get_server(self, server_ip):
        if self.exists_server_ip(server_ip):
            server = self.servers_c.execute("SELECT * FROM servers WHERE server_ip = ?", [server_ip]).fetchone()
            return server
        return None

    def get_server_settings(self, server_ip):
        if self.exists_server_ip(server_ip):
            server = self.get_server(server_ip)
            priv, permanent = bool(server[2]), bool(server[3]) # Better readability
            return [priv, permanent]
        return None

    def get_server_status(self, server_ip):
        if self.exists_server_ip(server_ip):
            server = self.get_server(server_ip)
            last_update, last_access = server[4], server[5]
            return [last_update, last_access]
        return None

    def get_server_access_count(self, server_ip):
        if self.exists_server_ip(server_ip):
            server = self.get_server(server_ip)
            access_count = server[6]
            return access_count # No list just a var
        return None

    def exists_server_id(self, server_id):
        return bool(self.servers_c.execute("SELECT * FROM servers WHERE id = ?", [server_id]).fetchall())

    def get_server_ip(self, server_id):
        return self.servers_c.execute("SELECT * FROM servers WHERE id = ?", [server_id]).fetchone()[1]

    def get_server_id(self, server_ip):
        return self.get_server(server_ip)[0]

    def add_tracking_point(self, server_ip, timestamp, latency, players):
        if self.exists_server_ip(server_ip):
            server = [self.get_server_id(server_ip), timestamp, latency, players]
            self.servers_c.execute("INSERT INTO tracking_points (server_id, timestamp, latency, players) VALUES (?, ?, ?, ?)", server)
            self.servers.commit()

    def get_tracking_points(self, server_ip):
        server_id = self.get_server_id(server_ip)
        tracking_points = self.servers_c.execute("SELECT * FROM tracking_points WHERE server_id = ?", [server_id])
        tracking_point = tracking_points.fetchone()
        results = []
        while tracking_point:
            results.append(tracking_point)
            tracking_point = tracking_points.fetchone()
        return results