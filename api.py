from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse

from mcstatus_handler import server as mcs

app = FastAPI()

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/server/{server_ip}/players")
def read_server(server_ip: str):
    return {mcs(server_ip).players.online}

@app.get("/server/{server_ip}/players/max")
def read_server(server_ip: str):
    return {mcs(server_ip).players.max}

@app.get("/server/{server_ip}/icon")
def read_server(server_ip: str):
    return {mcs(server_ip).icon}

@app.get("/server/{server_ip}/modt")
def read_server(server_ip: str):
    modt = mcs(server_ip).modt
    return [str(item) for item in modt] # convert list item to string