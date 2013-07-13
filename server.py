from bottle import route, run, static_file
from bottle import get, post, request, response

from settings import *
from game import Game

@get('/')
def index():
    return static_file('index.html', root=STATIC_FILES_DIR)

@post('/startwithconfig')
def start_game():
    """
    expects:
    {
        player_urls: [
            'url to snake client endpoint', ...
        ],
        local_player: true|false,
        width: 100,
        height: 100
    }
    """
    data = request.json

    game = Game(player_urls=data.player_urls,
            local_player=data.local_player,
            width=data.width,
            height=data.height)

    response.content_type = 'application/json'
    return dumps(game.to_dict())

@post('/uidotick')
def tick():
    """
    expects:
    {
        game_id: "unique-id-for-game",
        local_player_move: "n|w|s|e"
    }
    """
    data = request.json

    game = Game(data.game_id)

    game.tick(local_player_move=data.local_player_move)

    response.content_type = 'application/json'
    return dumps(game.to_dict())

run(host='localhost', port=8080)

