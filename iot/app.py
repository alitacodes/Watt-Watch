from flask import Flask, request, jsonify

app = Flask(__name__)

# Initial State Registry for both rooms
# Room 0: 3 appliances | Room 1: 4 appliances
device_states = {
    "0": {"e0": 0, "e1": 0, "e2": 0},
    "1": {"e0": 0, "e1": 0, "e2": 0, "e3": 0}
}

# 1. Endpoint for ESP32 to fetch current targets (Polling)
@app.route('/get_commands/<room_id>', methods=['GET'])
def get_commands(room_id):
    if room_id in device_states:
        return jsonify(device_states[room_id]), 200
    return jsonify({"error": "Room not found"}), 404

# 2. Endpoint for ESP32 to report its actual status
@app.route('/report_state', methods=['POST'])
def report_state():
    data = request.json
    room = str(data.get("room"))
    appl = data.get("appliance")
    state = data.get("state")
    
    if room in device_states and appl in device_states[room]:
        print(f"Room {room} | {appl} confirmed state: {state}")
        return jsonify({"status": "received"}), 200
    return jsonify({"status": "error"}), 400

# 3. User Control URL: http://<IP>:5000/control/1/e3/1
@app.route('/control/<int:room>/<string:appl>/<int:state>')
def control_pin(room, appl, state):
    r_str = str(room)
    if r_str in device_states and appl in device_states[r_str]:
        device_states[r_str][appl] = state
        return jsonify({"message": f"Command set: Room {room}, {appl} -> {state}"})
    return jsonify({"message": "Invalid Room or Appliance"}), 404

if __name__ == '__main__':
    # Use 0.0.0.0 so ESP32 can connect via your local IP
    app.run(host='0.0.0.0', port=5000, debug=True)