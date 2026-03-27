from flask import Flask, Response
from server import *

app = Flask(__name__)

@app.route('/')
def index():
    return "hello world"

@app.route("/test")
def test():
    pass

if __name__ == "__main__":
    app.run(debug=True)