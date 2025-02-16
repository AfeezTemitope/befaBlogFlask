from flask import Blueprint

from auth import requires_auth
from views.playerView import create_player, get_player

befa = Blueprint('befa', __name__)


@befa.post('/player')
@requires_auth
def create_potm_route():
    return create_player()


@befa.get('/player')
def get_players_routes():
    return get_player()