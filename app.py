import json
import logging
from typing import List, Dict

from flask import Flask
from flask_socketio import SocketIO, emit

from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
socket_io = SocketIO(app=app, cors_allowed_origins='*')

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('Selenium app')
logger.setLevel(logging.INFO)

user_actions: List[Dict[str, any]] = []


@socket_io.on('connect')
def handle_connect():
    logger.info("Client connected...")
    emit("connection_established", "Server connected")


@socket_io.on('keyPress')
def key_press_handler(data: Dict[str, any]):
    logger.info("Key press event received")
    user_actions.append({
        'event': 'keyPress',
        **data
    })


@socket_io.on('click')
def key_press_handler(data: Dict[str, any]):
    logger.info("Click event received")
    user_actions.append({
        'event': 'click',
        **data
    })


@socket_io.on('scroll')
def key_press_handler(data: Dict[str, any]):
    logger.info("Scroll event received")
    user_actions.append({
        'event': 'scroll',
        **data
    })


def save_actions():
    logger.info("Saving actions...")
    try:
        with open('./actions.json', 'r+') as actions_file:
            file_data = actions_file.read()
            try:
                stored_user_actions = json.loads(file_data)['user_actions']
                if len(user_actions):
                    stored_user_actions.extend(user_actions)
                    actions_file.seek(0)
                    actions_file.write(json.dumps({'user_actions': stored_user_actions}))
            except json.decoder.JSONDecodeError:
                actions_file.write(json.dumps({'user_actions': user_actions}))
    except FileNotFoundError:
        with open('./actions.json', 'w') as actions_file:
            actions_file.write(json.dumps({'user_actions': user_actions}))

    user_actions.clear()


scheduler = BackgroundScheduler()
scheduler.add_job(func=save_actions, trigger="interval", seconds=10)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    socket_io.run(app=app)
