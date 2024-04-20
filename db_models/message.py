from repository.database import db

class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  message = db.Column(db.String(500), nullable=False)
  room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
