from flask import Flask, request, jsonify
from db import get_db_connection

import pymysql
import logging
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 25060))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

con = get_db_connection()

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World! This is the backend server for Watt Watch."

@app.get('/api/v1/check_user/<userid>')
def check_user(userid):
    query = "SELECT userid FROM users WHERE userid = %s"
    with con.cursor() as cursor:
        cursor.execute(query, (userid,))
        result = cursor.fetchone()
    print(result)
    if result is None:
        return {"exists": False}
    return {"exists": True}

@app.post('/api/v1/add_user/<userid>')
def add_user(userid):
    request_data = request.get_json()
    password = request_data.get("password")
    type = request_data.get("type")
    query = "INSERT INTO users (userid, password, type) VALUES (%s, %s, %s)"
    try:
        with con.cursor() as cursor:
            cursor.execute(query, (userid, password, type))
        con.commit()
        return jsonify({"message": "User added successfully"}), 200
    except pymysql.MySQLError as e:
        logging.error(f"Error adding user to database: {e}")
        return jsonify({"error": "Failed to add user"}), 500
        

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)