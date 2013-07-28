# Required to make bottle work with gevent
import gevent.monkey
import json
gevent.monkey.patch_all()

from bson.json_util import dumps

from bottle import debug, get, put, post, request, response, run, static_file

from settings import *
from game import Game, Highscores


@get('/')
def index():
    return static_file('index.html', root=STATIC_FILES_DIR)


@get('/js/<filename>')
def server_js(filename):
    return static_file(filename, root=STATIC_FILES_DIR+'/js')


@get('/css/<filename>')
def server_css(filename):
    return static_file(filename, root=STATIC_FILES_DIR+'/css')


@get('/favicon.ico')
def favicon():
    return static_file('favicon.gif', root=STATIC_FILES_DIR)


@get('/game/<game_id>')
def get_game_state(game_id):
    game = Game(game_id)
    return json.dumps(game.get_state())

@get('/highscores')
def get_highscores():
    return static_file('highscores.html', root=STATIC_FILES_DIR)

@get('/highscores/players')
def get_player_scores():
    hs = Highscores()
    return dumps(hs.get_players()[:])

@get('/highscores/games')
def get_game_scores():
    hs = Highscores()
    return dumps(hs.get_games()[:])

@post('/game')
def create_game():
    """
    expects:
    {
        local_player: true|false,
        width: 100,
        height: 100
    }
    """
    data = request.json

    game = Game(
        local_player=data['local_player'],
        width=data['width'],
        height=data['height']
    )

    game.save()

    response.content_type = 'application/json'
    return json.dumps(game.get_state())


@put('/game.addplayerurl/<game_id>')
def add_player(game_id):
    """
    expects:
    {
        player_url: "http://my-url-endpoint"
    }
    """

    data = request.json

    if 'player_url' not in data:
        abort(400, "player_url must be passed in request body")
        return

    game = Game(game_id)
    player = game.add_player(data['player_url'])

    return json.dumps(player)


@put('/game.start/<game_id>')
def start_game(game_id):
    """
    expects: N/A
    """

    game = Game(game_id)
    game.do_client_start()
    return json.dumps(game.get_state())


@put('/game.tick/<game_id>')
def tick(game_id):
    """
    expects:
    {
        local_player_move: {
            player_id: <SOMETHING>,
            move: "n|w|s|e"
        }
    }
    """
    data = request.json

    game = Game(game_id=data['game_id'])

    if 'local_player_move' in data:
        game.tick(local_player_move=data['local_player_move'])
    else:
        game.tick()

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
        run(host='localhost', port=8002)
