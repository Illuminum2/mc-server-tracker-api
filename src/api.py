from logging import warning

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference
from pydantic import BaseModel

import time

from src.db_handler import DBHandler
from src.mcstatus_handler import (Server as mcs)
from src.constants import API_ROOT_PATH, MC_PORT

description = """
This is a simple API that let's you track the player count of a java minecraft server.
There is also functionality for requesting other information.
"""

tags_metadata = [
    {
        "name": "Tracking",
        "description": "All endpoint related to server tracking"
    },
    {
        "name": "Info",
        "description": "Other endpoints related to fetching information about servers"
    }
]

app = FastAPI(
    root_path=API_ROOT_PATH,
    openapi_tags=tags_metadata,
    docs_url=None,
    redoc_url=None,
    title="Minecraft Server Tracking API",
    description=description,
    version="0.1.0",
    license_info={
    "name": "MIT",
    "url": "https://opensource.org/licenses/MIT",
}
)

class Server(BaseModel):
    ip: str
    port: int | None = MC_PORT
    private: bool | None = False

@app.get("/", include_in_schema=False)
async def read_root():
    return RedirectResponse(url=f"{app.root_path}/docs")

@app.get("/scalar", include_in_schema=False)
async def read_root():
    return RedirectResponse(url=f"{app.root_path}/docs")

@app.get("/v1/", include_in_schema=False)
async def read_v1_root():
    return RedirectResponse(url=f"{app.root_path}/docs")

@app.get("/v1/scalar", include_in_schema=False)
async def v1_scalar_redirect():
    return RedirectResponse(url=f"{app.root_path}/docs")

@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

@app.get("/v1/tracking/list", tags=["Tracking"], name="Tracked Servers List")
async def read_server_list():
    try:
        db = DBHandler()
        servers = db.servers.ips_public()
        return {"servers": servers if servers else None}
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/v1/tracking/count", tags=["Tracking"], name="Tracked Servers Count")
async def read_server_count():
    try:
        db = DBHandler()
        count = db.servers.count_public
        return {"servers": count if count else None}
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/v1/tracking/{server_ip}/all", tags=["Tracking"], name="Tracking Data For Server", description="A tracking point is in the format [Timestamp, Latency(ms), Player_Count]")
async def read_server_tracking_data(server_ip: str):
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

@app.post("/v1/tracking/add", tags=["Tracking"], name="Track Server")
async def add_server_tracking(server: Server):
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

@app.get("/v1/server/{server_ip}/players/online", tags=["Info"], name="Server Players Online")
async def read_server_players_online(server_ip: str):
    players = mcs(server_ip).players
    return {"online": players.online if players else None}

@app.get("/v1/server/{server_ip}/players/max", tags=["Info"], name="Server Players Max")
async def read_server_players_max(server_ip: str):
    players = mcs(server_ip).players
    return {"max": players.max if players else None}

@app.get("/v1/server/{server_ip}/version/name", tags=["Info"], name="Server Version Name")
async def read_server_version_name(server_ip: str):
    version = mcs(server_ip).version
    return {"version": version.name if version else None}

@app.get("/v1/server/{server_ip}/version/protocol", tags=["Info"], name="Server Version Protocol")
async def read_server_version_protocol(server_ip: str):
    version = mcs(server_ip).version
    return {"protocol": version.protocol if version else None}

@app.get("/v1/server/{server_ip}/enforces_secure_chat", tags=["Info"], name="Server Enforces Secure Chat")
async def read_server_enforces_secure_chat(server_ip: str):
    enforce_secure_chat = mcs(server_ip).enforces_secure_chat
    return {"enforces_secure_chat": enforce_secure_chat if enforce_secure_chat else None}

@app.get("/v1/server/{server_ip}/latency", tags=["Info"], name="Server Latency")
async def read_server_latency(server_ip: str):
    latency = mcs(server_ip).latency
    return {"latency": latency if latency else None}

@app.get("/v1/server/{server_ip}/modt/minecraft", tags=["Info"], name="Server Message Of The Day")
async def read_server_modt_minecraft(server_ip: str):
    modt = mcs(server_ip).modt
    return {"modt_minecraft": [str(message) for message in modt] if modt else None}

@app.get("/v1/server/{server_ip}/icon", tags=["Info"], name="Server Icon")
async def read_server_icon(server_ip: str):
    icon = mcs(server_ip).icon
    return {"icon": icon if icon else None}

@app.get("/v1/server/{server_ip}/software/version", tags=["Info"], name="Server Software Version", description="Warning: This uses query which may be slow if the server has querying disabled")
async def read_server_software_version(server_ip: str):
    software = mcs(server_ip).software
    return {"version_sw": software.version if software else None}

@app.get("/v1/server/{server_ip}/software/brand", tags=["Info"], name="Server Software Brand", description="Warning: This uses query which may be slow if the server has querying disabled")
async def read_server_software_brand(server_ip: str):
    software = mcs(server_ip).software
    return {"brand_sw": software.brand if software else None}

@app.get("/v1/server/{server_ip}/software/plugins", tags=["Info"], name="Server Software Plugins", description="Warning: This uses query which may be slow if the server has querying disabled")
async def read_server_software_plugins(server_ip: str):
    software = mcs(server_ip).software
    return {"plugins": [str(plugin) for plugin in software.plugins] if software else None}

@app.get("/v1/server/{server_ip}/map/name", tags=["Info"], name="Server Map Name", description="Warning: This uses query which may be slow if the server has querying disabled")
async def read_server_map_name(server_ip: str):
    map = mcs(server_ip).map
    return {"map_name": map if map else None}