from flask import Blueprint
from auth import requires_auth, login
from views.clubAnnouncement import club_announcement, get_club_announcement
from views.playerView import create_player, get_player
from views.trainingView import create_training_day, get_training_schedule

befa = Blueprint('befa', __name__)


@befa.post('/login')
def login_route():
    return login()


@befa.post('/player')
@requires_auth
def create_potm_route():
    return create_player()


@befa.get('/player')
def get_players_routes():
    return get_player()


@befa.post('/schedule')
@requires_auth
def create_training_route():
    return create_training_day()


@befa.get('/schedule')
def get_schedule_route():
    return get_training_schedule()


@befa.post('/club-announcement')
@requires_auth
def post_club_announcement():
    return club_announcement()


@befa.get('/club-announcement')
def get_befa_announcement():
    return get_club_announcement()
