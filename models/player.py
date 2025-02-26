import json

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    image_urls = db.Column(db.JSON, nullable=False)
    is_potm = db.Column(db.Boolean, default=False)

    def __init__(self, name, position, image_urls, is_potm=False):
        self.name = name
        self.position = position
        self.image_urls = image_urls
        self.is_potm = is_potm

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'image_urls': self.image_urls,
            'is_potm': self.is_potm
        }


class TrainingDay(db.Model):
    __tablename__ = 'training_days'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    jersey_color = db.Column(db.String(20), nullable=False)

    def __init__(self, day, date, time, venue, jersey_color):
        self.day = day
        self.date = date
        self.time = time
        self.venue = venue
        self.jersey_color = jersey_color

    def to_dict(self):
        return {
            'id': self.id,
            'day': self.day,
            'date': self.date,
            'time': self.time,
            'venue': self.venue,
            'jersey_color': self.jersey_color
        }
