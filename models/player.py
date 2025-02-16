from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_potm = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'position': self.position,
            'image_url': self.image_url,
            'is_potm': self.is_potm,
        }
