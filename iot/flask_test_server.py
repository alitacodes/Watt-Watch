import asyncio
import websockets
import json

HOST = "0.0.0.0"
PORT = 8765

connected_clients = set()
# Format: {(roomno, applno): 1 (ON) or 0 (OFF)}
STATE_REGISTRY = {}  

def get(roomno, applno):
    """Returns 1 (ON) or 0 (OFF). Defaults to 0."""
    return STATE_REGISTRY.get((int(roomno), str(applno)), 0) 

def command(roomno, applno, comman_d):
    """Logic based on integer command (1=ON, 0=OFF)."""
    current_state = get(roomno, applno) 
    comman_d = int(comman_d)
    
    if current_state == 1 and comman_d == 1:
        return {"status": "already on", "send": False}
    elif current_state == 0 and comman_d == 0:
        return {"status": "already off", "send": False}
    elif current_state == 1 and comman_d == 0:
        new_status = 0
        status_msg = "appl off"
    elif current_state == 0 and comman_d == 1:
        new_status = 1
        status_msg = "appl on"
    
    return {
        "action": "SET_STATE",
        "room": int(roomno),
        "appliance": str(applno),
        "state": new_status,
        "status": status_msg,
        "send": True
    } 

# Shared broadcast function for Flask and WebSocket handler
async def broadcast_command(instr):
    if connected_clients:
        message = json.dumps(instr)
        await asyncio.gather(*[c.send(message) for c in connected_clients]) 

async def handler(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            # Store state with room number and appliance ID
            STATE_REGISTRY[(int(data['room']), str(data['appliance']))] = int(data['state']) 
            print(f"[Sync] Room {data['room']} | {data['appliance']} is {data['state']}")
    finally:
        connected_clients.discard(websocket)

async def start_ws_server():
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()  # Run forever

# ... (all your get, command, and handler functions) ...

async def main():
    print(f"[*] WebSocket server starting on ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()  # This keeps the server running forever


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n[*] Server stopped.")