from repository.database import db

class Room(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  messages = db.relationship('Message', backref='room', lazy=True)
