from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import os
from functools import wraps

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise ValueError("Admin username and password must be set as environment variables.")

hashed_admin_password = generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256')


def authenticate(username, password):
    if username == ADMIN_USERNAME and check_password_hash(hashed_admin_password, password):
        return True
    return False


def requires_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not authenticate(auth.username, auth.password):
            return jsonify({'message': 'Authentication required'}), 401
        return f(*args, **kwargs)

    return decorated


def login():
    auth = request.authorization
    if auth and authenticate(auth.username, auth.password):
        return jsonify({'message': 'login successful'}), 200
    return jsonify({'message': 'invalid credentials'}), 401
