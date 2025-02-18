from flask import Blueprint
from auth import requires_auth, login, check_auth
from views.playerView import create_player, get_player

befa = Blueprint('befa', __name__)


@befa.post('/login')
def login_route():
    return login()


@befa.route('/check-auth')
def check_auth_route():
    return check_auth()


@befa.post('/player')
@requires_auth
def create_potm_route():
    return create_player()


@befa.get('/player')
def get_players_routes():
    return get_player()
