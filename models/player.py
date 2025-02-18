from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.JSON, nullable=False)

    def __init__(self, name, position, image_url):
        self.name = name
        self.position = position
        self.image_url = image_url
