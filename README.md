# Minecraft Server Tracker API

A FastAPI application that tracks Minecraft servers and provides an API to access server status and player counts.

## Features

- Track multiple Minecraft servers
- Store historical player count and latency data
- Query server details (version, plugins, latency, etc.)
- Public and private server tracking

## API Endpoints

### Tracking
- `GET /api/v1/tracking/list` - List all public server IPs that are being tracked
- `GET /api/v1/tracking/count` - Get total number of public servers that are being tracked
- `GET /api/v1/tracking/{server_ip}/all` - Get historical player count and latency data
- `POST /api/v1/tracking/add` - Add a server to track, private controls visibility when calling the `/api/v1/tracking/list` endpoint
  ```json
  {
    "ip": "mc.example.com",
    "port": 25565,
    "private": false
  }
  ```

### Server Info
- `GET /api/v1/server/{server_ip}/players/online` - Get current player count
- `GET /api/v1/server/{server_ip}/players/max` - Get max player capacity
- `GET /api/v1/server/{server_ip}/version/name` - Get server version name
- `GET /api/v1/server/{server_ip}/version/protocol` - Get protocol version
- `GET /api/v1/server/{server_ip}/enforces_secure_chat` - Check if secure chat is enforced
- `GET /api/v1/server/{server_ip}/latency` - Get server latency
- `GET /api/v1/server/{server_ip}/modt/minecraft` - Get server message of the day in minecraft format
- `GET /api/v1/server/{server_ip}/icon` - Get server icon
- `GET /api/v1/server/{server_ip}/software/version` - Get software version
- `GET /api/v1/server/{server_ip}/software/brand` - Get server software brand
- `GET /api/v1/server/{server_ip}/software/plugins` - Get server plugins
- `GET /api/v1/server/{server_ip}/map/name` - Get map name

## API Documentation
Access Scalar API documentation at the `/mc/api/docs` after deployment.
