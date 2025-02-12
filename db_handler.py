import sqlite3
from time import time

class DBHandler:
    def __init__(self, servers_db_path):
        self.servers = sqlite3.connect(servers_db_path)
        self.servers_c = self.servers.cursor()
        self.servers.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                priv INTEGER NOT NULL,
                permanent INTEGER NOT NULL,
                last_update INTEGER,
                last_access INTEGER NOT NULL,
                access_count INTEGER
            );
        """)
        self.servers.execute("""
            CREATE TABLE IF NOT EXISTS tracking_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                timestamp INTEGER NOT NULL,
                latency INTEGER,
                players INTEGER,
                FOREIGN KEY (server_id) REFERENCES servers(id)  -- Foreign key(server_id) linking to id of servers table
            );
        """)
        self.servers.commit()

    def add_server(self, server_ip, private, permanent):
        if not self.server_exists(server_ip):
            server = [server_ip, private, permanent, int(time()), 1]
            self.servers_c.execute("INSERT INTO servers (ip, priv, permanent, last_access, access_count) VALUES (?, ?, ?, ?, ?)", server)
            self.servers.commit()

    def server_exists(self, server_ip):
        return bool(self.servers_c.execute("SELECT * FROM servers WHERE ip = ?", [server_ip]).fetchall()) # If list is empty bool() returns False

    def get_server_settings(self, server_ip):
        if self.server_exists(server_ip):
            server = self.servers_c.execute("SELECT * FROM servers WHERE ip = ?", [server_ip]).fetchone()
            priv, permanent = bool(server[2]), bool(server[3]) # Better readability
            return [priv, permanent]

    def server_exists(self, server_ip):
        if self.server_exists(server_ip):
            server = self.servers_c.execute("SELECT * FROM servers WHERE ip = ?", [server_ip]).fetchone()
            last_update, last_access = server[4], server[5]
            return [last_update, last_access]

    def server_exists(self, server_ip):
        if self.server_exists(server_ip):
            server = self.servers_c.execute("SELECT * FROM servers WHERE ip = ?", [server_ip]).fetchone()
            access_count = server[6]
            return access_count # No list just a var

