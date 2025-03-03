from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

from db_handler import DBHandler
from mcstatus_handler import Server as mcs

app = FastAPI()
db = DBHandler()

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/scalar")

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

@app.get("/server/{server_ip}/players/online")
def read_server_players_online(server_ip: str):
    players = mcs(server_ip).players
    return {"online": players.online if players else None}

@app.get("/server/{server_ip}/players/max")
def read_server_players_max(server_ip: str):
    players = mcs(server_ip).players
    return {"max": players.max if players else None}

@app.get("/server/{server_ip}/version/name")
def read_server_version_name(server_ip: str):
    version = mcs(server_ip).version
    return {"version": version.name if version else None}

@app.get("/server/{server_ip}/version/protocol")
def read_server_version_protocol(server_ip: str):
    version = mcs(server_ip).version
    return {"version": version.protocol if version else None}

@app.get("/server/{server_ip}/software/version")
def read_server_software_version(server_ip: str):
    software = mcs(server_ip).software
    return {"version": software.version if software else None}

@app.get("/server/{server_ip}/software/brand")
def read_server_software_brand(server_ip: str):
    software = mcs(server_ip).software
    return {"version": software.brand if software else None}

@app.get("/server/{server_ip}/software/plugins")
def read_server_software_plugins(server_ip: str):
    software = mcs(server_ip).software
    return {"plugins": [str(plugin) for plugin in software.plugins] if software else None}

@app.get("/server/{server_ip}/icon")
def read_server_icon(server_ip: str):
    icon = mcs(server_ip).icon
    return {"icon": icon if icon else None}

@app.get("/server/{server_ip}/modt/minecraft")
def read_server_modt_minecraft(server_ip: str):
    modt = mcs(server_ip).modt
    return {"modt minecraft": [str(message) for message in modt] if modt else None}

@app.get("/server/{server_ip}/map/name")
def read_server_map_name(server_ip: str):
    map = mcs(server_ip).map
    return {"map name": map if map else None}

@app.get("/server/{server_ip}/enforces_secure_chat")
def read_server_enforces_secure_chat(server_ip: str):
    enforce_secure_chat = mcs(server_ip).enforce_secure_chat
    return {"enforces_secure_chat": enforce_secure_chat if enforce_secure_chat else None}

@app.get("/server/{server_ip}/latency")
def read_server_latency(server_ip: str):
    latency = mcs(server_ip).latency
    return {"latency": latency if latency else None}

#@app.get("/server/{server_ip}/tracking-points")
#def read_server_tracking_points(server_ip: str):
#    return db.tracking_points.get(server_ip)