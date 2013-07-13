from json import dumps
from uuid import uuid4

from bottle import route, run, static_file
from bottle import get, post, request, response

from settings import *

@get('/')
def ui_index():
    return static_file('index.html', root=STATIC_FILES_DIR)

@post('/game/uistart')
def ui_start_game():
    """
    expects:
    {
        player_urls: [
            'url to snake client endpoint', ...
        ],
        local_player: true|false
    }
    """
    response.content_type = 'application/json'
    data = request.json

    # init game state
    # return a game id
    game_state = {
        "id": uuid4().urn
    }

    return dumps(game_state)

@post('/game/tick')
def ui_tick():
    """
    expects:
    {
        game_id: "unique-id-for-game",
        local_player_move: "n|w|s|e"
    }
    """
    response.content_type = 'application/json'
    data = request.json



    # init game state
    # return a game id
    game_state = {
        "id": data.game_id
    }

    return dumps(game_state)


run(host='localhost', port=8080)

