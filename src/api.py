from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference
from pydantic import BaseModel

import time

from src.db_handler import DBHandler
from src.mcstatus_handler import (Server as mcs)
from src.constants import API_ROOT_PATH, MC_PORT

app = FastAPI(root_path=API_ROOT_PATH)

class Server(BaseModel):
    ip: str
    port: int | None = MC_PORT
    private: bool | None = False

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url=f"{app.root_path}/scalar")

@app.get("/v1/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

@app.get("/v1/server/list")
def read_server_list():
    try:
        db = DBHandler()
        servers = db.servers.ips_public()
        return {"servers": servers if servers else None}
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/v1/server/count")
def read_server_count():
    try:
        db = DBHandler()
        count = db.servers.count_public
        return {"servers": count if count else None}
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/v1/server/{server_ip}/players/online")
def read_server_players_online(server_ip: str):
    players = mcs(server_ip).players
    return {"online": players.online if players else None}

@app.get("/v1/server/{server_ip}/players/max")
def read_server_players_max(server_ip: str):
    players = mcs(server_ip).players
    return {"max": players.max if players else None}

@app.get("/v1/server/{server_ip}/version/name")
def read_server_version_name(server_ip: str):
    version = mcs(server_ip).version
    return {"version": version.name if version else None}

@app.get("/v1/server/{server_ip}/version/protocol")
def read_server_version_protocol(server_ip: str):
    version = mcs(server_ip).version
    return {"protocol": version.protocol if version else None}

@app.get("/v1/server/{server_ip}/software/version")
def read_server_software_version(server_ip: str):
    software = mcs(server_ip).software
    return {"version_sw": software.version if software else None}

@app.get("/v1server/{server_ip}/software/brand")
def read_server_software_brand(server_ip: str):
    software = mcs(server_ip).software
    return {"brand_sw": software.brand if software else None}

@app.get("/v1/server/{server_ip}/software/plugins")
def read_server_software_plugins(server_ip: str):
    software = mcs(server_ip).software
    return {"plugins": [str(plugin) for plugin in software.plugins] if software else None}

@app.get("/v1/server/{server_ip}/icon")
def read_server_icon(server_ip: str):
    icon = mcs(server_ip).icon
    return {"icon": icon if icon else None}

@app.get("/v1/server/{server_ip}/modt/minecraft")
def read_server_modt_minecraft(server_ip: str):
    modt = mcs(server_ip).modt
    return {"modt_minecraft": [str(message) for message in modt] if modt else None}

@app.get("/v1/server/{server_ip}/map/name")
def read_server_map_name(server_ip: str):
    map = mcs(server_ip).map
    return {"map_name": map if map else None}

@app.get("/v1/server/{server_ip}/enforces_secure_chat")
def read_server_enforces_secure_chat(server_ip: str):
    enforce_secure_chat = mcs(server_ip).enforce_secure_chat
    return {"enforces_secure_chat": enforce_secure_chat if enforce_secure_chat else None}

@app.get("/v1/server/{server_ip}/latency")
def read_server_latency(server_ip: str):
    latency = mcs(server_ip).latency
    return {"latency": latency if latency else None}

@app.get("/v1/tracking/{server_ip}/all")
def read_server_tracking_data(server_ip: str):
    if ":" not in server_ip:
        full_address = f"{server_ip}:{MC_PORT}"
    else:
        full_address = server_ip

    db = DBHandler()
    if db.servers.exists_ip(full_address):
        data = db.tracking_points.get(full_address)
        db.servers.update_access(full_address, int(time.time()))
        return {"tracking_points": data if data else None}
    else:
        raise HTTPException(status_code=404, detail="Server not found")

@app.post("/v1/tracking/add")
def add_server_tracking(server: Server):
    address = f"{server.ip}:{str(server.port)}"
    status = mcs(address).status
    if not status is None:
        db = DBHandler()
        if not db.servers.exists_ip(address):
            db.servers.add(address, server.private, 0)
            return {"status": "success", "detail": "Server was added"}
            #raise HTTPException(status_code=200, detail="Server was added")
        else:
            raise HTTPException(status_code=403, detail="Server already exists") # Better status code would be
    else:
        raise HTTPException(status_code=404, detail="No connection can be made to the server")