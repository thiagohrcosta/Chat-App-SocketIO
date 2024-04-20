from flask import Flask, jsonify, request, send_file,render_template, redirect, url_for
from repository.database import db
from flask_socketio import SocketIO
from faker import Faker

from db_models import Room

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'SECRET_KEY_WEBSOCKET'

db.init_app(app)
fake = Faker()

# db.init_app(app)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

@app.route("/", methods=['GET'])
def chat():
  rooms = Room.query.all()
  return render_template('index.html', rooms=rooms)

@app.route('/', methods=['POST'])
def create():
  room_name = fake.word()
  new_room = Room(name=room_name)

  db.session.add(new_room)
  db.session.commit()

  return redirect(url_for('room', room_name=room_name))

@app.route('/room/<room_name>')
def room(room_name):
   return render_template(
    'room.html', 
    room_name=room_name
  )

@app.route("/<int:message_id>", methods=['GET'])
def message():
   return

# websockets
@socketio.on('connect')
def handle_connect():
  print('Client connected to the server')


@socketio.on('connect')
def handle_disconnect():
    print('Client has disconnected to the server')
    
if __name__ == '__main__':
   socketio.run(app, debug=True)