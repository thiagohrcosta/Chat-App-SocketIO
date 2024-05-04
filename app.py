from flask import Flask, jsonify, request, send_file,render_template, redirect, url_for
from repository.database import db
from flask_socketio import SocketIO, emit

from faker import Faker

from db_models.room import Room
from db_models.message import Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'SECRET_KEY_WEBSOCKET'

db.init_app(app)
fake = Faker()

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

@app.route('/room/<room_name>', methods=['GET'])
def room(room_name):
  room = Room.query.filter_by(name=room_name).first()
  messages = Message.query.filter_by(room_id=room.id).all()

  return render_template(
    'room.html', 
    room_name=room_name, 
    messages=messages,
    host='http://127.0.0.1:5000/room/<room_name>'
  )

@app.route("/message/<room_name>", methods=['POST'])
def create_message(room_name):
  room = Room.query.filter_by(name=room_name).first()
  if room:
    data = request.form.get('input')

    if data == "":
      return jsonify({'message': 'Error'}), 400
    
    new_message = Message(
        message=data,
        room_id=room.id
    )
    db.session.add(new_message)
    db.session.commit()

    socketio.emit('message', {'message': new_message.message, 'room': room_name}, room=room_name)
  
  # return data, 200
  return jsonify({'message': 'Message created successfully'}), 200

@app.route("/delete_room/<int:room_id>", methods=['POST'])
def delete_room(room_id):
  room = Room.query.get(room_id)
  if room:
    Message.query.filter_by(room_id=room.id).delete()
    db.session.delete(room)
    db.session.commit()
    return jsonify({'message': 'Room deleted successfully'}), 200
  else:
    return jsonify({'error': 'Room not found'}), 404
  
# websockets
@socketio.on('connect')
def handle_connect():
    print('Client connected to the server')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client has disconnected from the server')

@socketio.on('message')  # Fix the event name here
def handle_message(data):
    room_name = data['room']
    join_room(room_name) 
    new_message = Message.query.filter_by(room_id=data['room_id']).order_by(Message.id.desc()).first()
    emit('message', {'message': new_message.message, 'room': room_name}, room=room_name)

if __name__ == '__main__':
   socketio.run(app, debug=True)