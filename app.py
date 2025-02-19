import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

load_dotenv()

from config import Config
from models.player import db
from urls import befa

app = Flask(__name__)
app.config.from_object(Config)

cors = CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://befa-blog-flask.vercel.app/"]}})

db.init_app(app)

migrate = Migrate(app, db)


@app.route('/')
def home():
    return "Welcome"


app.register_blueprint(befa)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
