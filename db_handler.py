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
                last_ping INTEGER,
                last_accessed INTEGER NOT NULL,
                access_count INTEGER
            );
        """)
        self.servers.execute("""
            CREATE TABLE IF NOT EXISTS request_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                timestamp INTEGER,
                latency INTEGER,
                players INTEGER,
                FOREIGN KEY (server_id) REFERENCES servers(id)  -- Foreign key linking to id of servers table
            );
        """)
        self.servers.commit()

    def add_server(self, server_ip, private, permanent):
        server = self.servers_c.execute("SELECT * FROM servers WHERE ip = ?", [server_ip]).fetchall() # fetchall returns empty list if no results
        if not server:
            server = [server_ip, private, permanent, int(time()), 1]
            self.servers_c.execute("INSERT INTO servers (ip, priv, permanent, last_accessed, access_count) VALUES (?, ?, ?, ?, ?)", server)
            self.servers.commit()