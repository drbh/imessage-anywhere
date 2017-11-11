from flask import Flask, request
import os
import sys
import sqlite3
import datetime
import json
from main import *

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

DATA = dataGrabber()
conn = DATA.conn
poller = DataPoller(conn)
Mess = imessageRubyWrapper()

DEFAULT_ACCOUNT = "3478344775"

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route("/send", methods=['POST', 'OPTIONS'])
def send():
    """ { "message": "hey there!" } """
    text = request.form['param1']
    contact = DEFAULT_ACCOUNT
    print request.form['param1']
    Mess.command(text, contact)
    return json.dumps({"status":"sent"})

@app.route("/messages", methods=['POST', 'OPTIONS'])
def messages():
    """ { "handle_id": "5" } """
    print request.form['param1']
    list_messages = DATA.find_get_messages(request.form['param1'])
    return json.dumps(list_messages)

@socketio.on('my event', namespace='/test')
def test_message(message):
    if poller.check_new_message():
        print "SHOULD UPDATE"
        emit('new_message')

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print "Starting Sever... Port 5000"
    socketio.run(app, host='0.0.0.0', port='5000')