# Required to make bottle work with gevent
import gevent.monkey
import json
gevent.monkey.patch_all()

from json import dumps

from bottle import debug, get, post, request, response, run, static_file

from settings import *
from game import Game


@get('/')
def index():
    return static_file('index.html', root=STATIC_FILES_DIR)


@get('/js/<filename>')
def server_js(filename):
    return static_file(filename, root=STATIC_FILES_DIR+'/js')


@get('/css/<filename>')
def server_css(filename):
    return static_file(filename, root=STATIC_FILES_DIR+'/css')


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

    game = Game(
        player_urls=data['player_urls'],
        local_player=data['local_player'],
        width=data['width'],
        height=data['height']
    )

    response.content_type = 'application/json'
    return json.dumps(game.get_state())


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

    game = Game(game_id=data['game_id'])

    game.tick(local_player_move=data['local_player_move'])
    game.save()

    response.content_type = 'application/json'

    return json.dumps(game.get_state())


## Run Bottle Server ##
if __name__ == '__main__':
    prod_port = os.environ.get('PORT', None)

    if prod_port:
        # Assume Heroku
        run(host='0.0.0.0', port=int(prod_port), server='gevent')
    else:
        # Localhost
        debug(True)
        run(host='localhost', port=8080)
