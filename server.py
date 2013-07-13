from json import dumps
from uuid import uuid4

from bottle import route, run, static_file
from bottle import get, post, request, response

from settings import *
from game import Game

@get('/')
def index():
    return static_file('index.html', root=STATIC_FILES_DIR)

@post('/game/uistart')
def start_game():
    """
    expects:
    {
        player_urls: [
            'url to snake client endpoint', ...
        ],
        local_player: true|false
    }
    """
    data = request.json

    game = Game(player_urls=data.player_urls, local_player=data.local_player)
    game.save()

    response.content_type = 'application/json'
    return dumps(game.to_dict())

@post('/game/tick')
def tick():
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

