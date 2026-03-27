from flask import Flask, jsonify
import asyncio
import json
import websockets
from flask_test_server import *

app = Flask(__name__)

@app.route('/')
def index():
    return "Smart Home Server Active"

# # URL format: /test/roomno/applno/state
# @app.route("/test/<int:roomno>/<string:applno>/<int:state>")
# def test_command(roomno, applno, state):
#     # Get logic from server.py
#     result = command(roomno, applno, state)
    
#     # If state needs to change, broadcast to the ESP32
#     if result.get("send"):
#         payload = {
#             "action": result["action"],
#             "room": result["room"],
#             "appliance": result["appliance"],
#             "state": result["state"]
#         }
        
#         # Bridge Flask to the async WebSocket
#         try:
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             loop.run_until_complete(broadcast_command(payload))
#             loop.close()
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
    
#     return jsonify({
#         "message": result["status"], 
#         "room": roomno, 
#         "appliance": applno,
#         "target_state": state
#     })


@app.route("/test")
def test():


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True, port=5000)