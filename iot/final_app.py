from flask import Flask, jsonify, request, send_file
#the code final fpor esp
app = Flask(__name__)

# Shared JSON variable representing the 2 emulated rooms
states = {
    "0e0": 0, "0e1": 0, "0e2": 0,        # Room 0 (Emulated)
    "1e0": 0, "1e1": 0, "1e2": 0, "1e3": 0 # Room 1 (Emulated)
}

@app.route('/')
def dashboard():
    return send_file('index.html')

# ESP32 pings this to get the latest shared state
@app.route('/sync', methods=['POST'])
def sync():
    return jsonify(states)

# URL Format: http://<IP>:5000/0/e1/1
@app.route('/<room>/<appliance>/<int:state>')
def update_state(room, appliance, state):
    key = f"{room}{appliance}"
    if key in states:
        states[key] = state
        print(f"[Shared JSON] {key} updated to {state}")
        return jsonify({"status": "success", "current_json": states})
    return jsonify({"status": "error", "message": "Invalid mapping"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)