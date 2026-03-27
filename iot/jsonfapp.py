from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

# The Shared JSON using your exact new mapping
states = {
    "1e0": 0, "1e1": 0, "1e6": 0, # Room 1
    "2e2": 0, "2e4": 0, "2e5": 0  # Room 2
}

@app.route('/sync', methods=['POST'])
def sync():
    # ESP32 pings this to get the current "Source of Truth"
    return jsonify(states)

# New URL Format to match your request: /<room>/<appliance>/<state>
# Example: /2/e4/1 -> Key becomes "2e4"
@app.route('/<room>/<appliance>/<int:state>')
def update_state(room, appliance, state):
    key = f"{room}{appliance}"
    if key in states:
        states[key] = state
        print(f"[System] {key} is now {'ON' if state == 1 else 'OFF'}")
        return jsonify({"status": "success", "device": key, "state": state})
    return jsonify({"status": "error", "message": "Invalid mapping"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)