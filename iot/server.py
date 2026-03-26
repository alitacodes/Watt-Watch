import asyncio
import websockets

HOST = "0.0.0.0"   # listens on all interfaces
PORT = 8765

connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print(f"[+] ESP32 connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"[ESP32 says]: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("[-] ESP32 disconnected")
    finally:
        connected_clients.discard(websocket)

async def send_loop():
    """Type messages in terminal → broadcast to ESP32"""
    loop = asyncio.get_event_loop()
    while True:
        msg = await loop.run_in_executor(None, input, "Send to ESP32: ")
        if connected_clients:
            await asyncio.gather(*[c.send(msg) for c in connected_clients])
            print(f"[Sent]: {msg}")
        else:
            print("[!] No ESP32 connected yet")

async def main():
    print(f"[*] WebSocket server running on ws://{HOST}:{PORT}")
    print("[*] Waiting for ESP32 to connect...\n")
    async with websockets.serve(handler, HOST, PORT):
        await send_loop()

if __name__ == "__main__":
    asyncio.run(main())
