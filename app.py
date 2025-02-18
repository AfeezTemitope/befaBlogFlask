import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask_migrate import Migrate

load_dotenv()

from flask import Flask
from urls import befa
from config import Config
from models.player import db

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db.init_app(app)

app.register_blueprint(befa)
migrate = Migrate(app, db)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
