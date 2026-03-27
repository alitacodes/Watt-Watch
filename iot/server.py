import asyncio
import websockets
import json

HOST = "0.0.0.0"
PORT = 8765

connected_clients = set()
STATE_REGISTRY = {}  # Format: {(roomno, applno): 1 (ON) or 0 (OFF)}

def get(roomno, applno):
    """Returns 1 (ON) or 0 (OFF). Defaults to 0."""
    return STATE_REGISTRY.get((roomno, applno), 0)

def command(roomno, applno, comman_d):
    """Logic based on user integer command (1=ON, 0=OFF)."""
    current_state = get(roomno, applno)
    
    if current_state == 1 and comman_d == 1:
        print(f"[Result] Appliance {applno} is already on")
        return None
    elif current_state == 0 and comman_d == 0:
        print(f"[Result] Appliance {applno} is already off")
        return None
    elif current_state == 1 and comman_d == 0:
        print(f"[Result] appl off")
        new_status = 0
    elif current_state == 0 and comman_d == 1:
        print(f"[Result] appl on")
        new_status = 1
    
    return {
        "action": "SET_STATE",
        "room": roomno,
        "appliance": applno,
        "state": new_status
    }

async def handler(websocket):
    connected_clients.add(websocket)
    print(f"[+] Connection from {websocket.remote_address}")
    try:
        async for message in websocket:
            data = json.loads(message)
            # Store state as integer 1 or 0
            STATE_REGISTRY[(data['room'], data['appliance'])] = data['state']
            print(f"[Sync] {data['appliance']} is {data['state']}")
    finally:
        connected_clients.discard(websocket)

async def command_interface():
    loop = asyncio.get_event_loop()
    while True:
        # User enters e.g., "e0 1"
        user_input = await loop.run_in_executor(None, input, "Enter (appl command): ")
        parts = user_input.split()
        if len(parts) < 2 or not connected_clients: continue

        instr = command(0, parts[0], int(parts[1]))
        if instr:
            await asyncio.gather(*[c.send(json.dumps(instr)) for c in connected_clients])

async def main():
    async with websockets.serve(handler, HOST, PORT):
        await command_interface()

if __name__ == "__main__":
    asyncio.run(main())