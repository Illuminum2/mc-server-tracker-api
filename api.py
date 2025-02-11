from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

from mcstatus_handler import server as mcs

app = FastAPI()

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

@app.get("/server/{server_ip}/players")
def read_server_players(server_ip: str):
    return {mcs(server_ip).players.online}

@app.get("/server/{server_ip}/players/max")
def read_server_players_max(server_ip: str):
    return {mcs(server_ip).players.max}

@app.get("/server/{server_ip}/icon")
def read_server_icon(server_ip: str):
    return {mcs(server_ip).icon}

@app.get("/server/{server_ip}/modt")
def read_server_modt(server_ip: str):
    modt = mcs(server_ip).modt
    return [str(item) for item in modt] # convert list item to string