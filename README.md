# Minecraft Server Tracker API

A FastAPI application that tracks Minecraft servers and provides an API to access server status and player counts.

## Features

- Track multiple Minecraft servers
- Store historical player count and latency data
- Query server details (version, plugins, latency, etc.)
- Public and private server tracking

## API Endpoints

### Server Listing
- `GET /mc/api/v1/server/list` - List all public server IPs that are being tracked
- `GET /mc/api/v1/server/count` - Get total number of public servers that are being tracked

### Server Info
- `GET /mc/api/v1/server/{server_ip}/players/online` - Get current player count
- `GET /mc/api/v1/server/{server_ip}/players/max` - Get max player capacity
- `GET /mc/api/v1/server/{server_ip}/version/name` - Get server version name
- `GET /mc/api/v1/server/{server_ip}/version/protocol` - Get protocol version
- `GET /mc/api/v1/server/{server_ip}/software/version` - Get software version
- `GET /mc/api/v1/server/{server_ip}/software/brand` - Get server software brand
- `GET /mc/api/v1/server/{server_ip}/software/plugins` - List server plugins
- `GET /mc/api/v1/server/{server_ip}/latency` - Get server latency
- `GET /mc/api/v1/server/{server_ip}/icon` - Get server icon

### Tracking
- `GET /mc/api/v1/tracking/{server_ip}/all` - Get historical player count and latency data
- `POST /mc/api/v1/tracking/add` - Add a server to track
  ```json
  {
    "ip": "mc.example.com",
    "port": 25565,
    "private": false
  }
  ```

## API Documentation
Access Scalar API documentation at the `/mc/api/docs` after deployment.
