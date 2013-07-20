import json
import requests
from random import randint
from uuid import uuid4

import gevent
from gevent import monkey
monkey.patch_all(httplib=True)

from pymongo import MongoClient

from game_id import generate_game_id
import settings


def get_mongodb():
    if settings.MONGODB_URL:
        client = MongoClient(host=settings.MONGODB_URL)
    else:
        client = MongoClient(host='localhost', port=27017)

    return client[settings.MONGODB_DATABASE]


class Highscores(object):
    document = None
    _MONGODB_COLLECTION_NAME = 'highscores'

    def __init__(self, db=None):
        self._mongodb = get_mongodb()

        if db:
            self.db = db
        else:
            self.db = self._get_mongo_collection()

    def _get_mongo_collection(self):
        return self._mongodb[self._MONGODB_COLLECTION_NAME]

    def save(self):
        self.db.save(self.document)

    def get_or_create(self):
        self.document = self.db.find_one({"_id": "highscores"})

        if not self.document:
            id = self.db.insert({
                '_id': 'highscores',
                'id': 'highscores',
                'players': {}
            })

            self.document = self.db.find_one({"_id": "highscores"})

            # save new highscores
            self.save()

        return self.document

    def update(self, game):
        for player in game['state']['snakes']:
            if not player['name'] in self.document['players']:
                self.document['players'][player['name']] = {
                    'kills': 0,
                    settings.FOOD: 0,
                    'life': 0,
                    'wins': 0
                }

            player_scores = self.document['players'][player['name']]

            if player['status'] == 'alive':
                player_scores['wins'] += 1

            player_scores['kills'] += int(player['stats']['kills'])
            player_scores['life'] += int(player['stats']['life'])
            player_scores[settings.FOOD] += int(player['stats'][settings.FOOD])

        self.save()

class Game(object):

    document = None
    _MONGODB_COLLECTION_NAME = 'games'

    def __init__(self, game_id=None, local_player=None,
            width=None, height=None
        ):
        self._mongodb = get_mongodb()
        self.db = self._get_mongo_collection()

        self.created = False

        if not game_id:
            self.document = self._create_game(
                local_player,
                width,
                height
            )
        else:
            self.game_id = game_id
            self.document = self._fetch_game()

    def _turns_get(self):
        return self.document['state']['turn_num']

    ## Board Interactions ##

    def board_generate_new(self, width, height):
        return [[[] for x in range(width)] for y in range(height)]

    def _board_get(self):
        return self.document['state']['board']

    def board_add_piece(self, pos, piece):
        board = self._board_get()
        (x, y) = pos
        board[y][x].append(piece)

    def board_maybe_add_food(self):
        i = randint(0, settings.FOOD_CHANCE)
        if i == 0:
            empty = self.board_find_empty_square()
            empty.append({
                'type': 'food',
                'id': self._gen_id()
            })

    def board_remove_piece(self, pos, piece_id):
        board = self._board_get()
        (x, y) = pos

        piece_to_remove = None
        for piece in board[y][x]:
            if piece['id'] == piece_id:
                piece_to_remove = piece

        if piece_to_remove:
            board[y][x].remove(piece_to_remove)

    def board_place_snake(self, pos, snake_id):
        self.board_add_piece(pos, {
            'type': settings.SNAKE,
            'id': snake_id
        })

    def board_place_snake_head(self, pos, snake_id):
        self.board_add_piece(pos, {
            'type': settings.SNAKE_HEAD,
            'id': snake_id
        })

    def board_find_empty_square(self):
        board = self._board_get()
        empties = []
        for row in board:
            for square in row:
                if len(square) == 0:
                    empties.append(square)
        rand = randint(0, len(empties) - 1)
        return empties[rand]

    def board_place_food(self, pos, food_id):
        self.board_add_piece(pos, {
            'type': settings.FOOD,
            'id': food_id
        })

    def _create_game(self, local_player, width, height):
        self.game_id = generate_game_id()
        self.created = True

        # next setup inital game state
        state = {
            'id': self.game_id,  # Should this be in here too?
            'snakes': [],
            'board': self.board_generate_new(width, height),
            'turn_num': 0,
            'game_over': False
        }

        id = self.db.insert({
            'id': self.game_id,
            'local_player': local_player,
            'players': [],
            'state': state,
            'width': width,
            'height': height
        })

        return self.db.find_one({"_id": id})

    def _gen_snake_and_player(self, player_url):
        new_id = self._gen_id()

        # keep player url private
        player = {
            'url': player_url,
            'id': new_id,
        }

        # public player
        snake = {
            'id': new_id,
            'queue': [self._gen_start_position()]
        }
        snake['ate_last_turn'] = False
        snake['last_move'] = ''
        snake['name'] = 'n/a',
        snake['status'] = 'alive'
        snake['message'] = ''
        snake['stats'] = {
            'kills': 0,
            settings.FOOD: 0,
            'life': 0
        }

        return snake, player

    def _add_snake_to_board(self, snake):
        start_pos = snake['queue'][0]
        self.board_place_snake_head(start_pos, snake['id'])

    def _gen_start_position(self):
        return (
            randint(0, self.document['width'] - 1),
            randint(0, self.document['height'] - 1)
        )

    def _gen_id(self):
        return str(uuid4())

    def _get_mongo_collection(self):
        return self._mongodb[self._MONGODB_COLLECTION_NAME]

    def _fetch_game(self):
        doc = self.db.find_one({"id": self.game_id})
        return doc

    def _client_request(self, player, path, data):
        headers = {'Content-type': 'application/json'}
        r = requests.post(player['url'] + path, data=json.dumps(data), headers=headers)

        try:
            result = r.json()
        except Exception as e:
            result = None
        return result

    ## ADDS A NEW PLAYER API ENDPOINT TO THE GAME
    def add_player(self, player_url):

        ## CHECK FOR DUPLICATE URL ADD
        for player in self.document['players']:
            if player['url'] == player_url:
                return player

        ## CREATE SNAKE
        new_snake, new_player = self._gen_snake_and_player(player_url)

        ## CALL REGISTER API TO GET SNAKE NAME
        player_name = self.do_client_register(new_player)

        ## SET SNAKE NAME
        new_snake['name'] = player_name

        ## ADD SNAKE TO BOARD
        self._add_snake_to_board(new_snake)

        ## UPDATE DOC
        self.document['players'].append(new_player)
        self.document['state']['snakes'].append(new_snake)

        self.save()

        return new_player

    def do_client_register(self, player):
        """ Register a new AI, return AI name """
        register_data = {
            'game_id': self.game_id,
            'client_id': player['id'],
            'board': {
                'width': self.document['width'],
                'height': self.document['height']
            }
        }

        if player['url'] == settings.LOCAL_PLAYER_URL:
            player_name = 'Local Snake'
        else:
            response = self._client_request(player, 'register', register_data)
            player_name = response['name']

        return player_name

    def do_client_start(self):
        """Starts all the clients asynchronously"""
        def client_start(player):
            data = {'game_id': self.game_id}
            return self._client_request(player, 'start', data)

        events = [gevent.spawn(client_start, player) for player in self.document['players']]
        gevent.joinall(events)

    def save(self):
        """saves game to mongo"""
        return self.db.save(self.document)

    def resolve_food(self):
        pass

    def _get_snake(self, snake_id):
        for snake in self.document['state']['snakes']:
            if snake['id'] == snake_id:
                return snake
        return None

    def _give_food(self, snake_id):
        # give food to this snake
        snake = self._get_snake(snake_id)
        snake['stats'][settings.FOOD] += 1
        snake['ate_last_turn'] = True

    def _give_kill(self, snake_id):
        # give kills to this snake
        snake = self._get_snake(snake_id)
        snake['stats']['kills'] += 1

    def player_compute_move(self, player, move):
        coords = player['queue'][-1]  # head
        player_id = player['id']
        x = coords[0]
        y = coords[1]

        old_x = x
        old_y = y

        result = {
            'new_head': None,
            'old_head': (old_x, old_y, player_id),
            'tail': None,
            'kill': False
        }

        # update player queue and board state with new head
        if move == 'n':
            y = y - 1
        elif move == 'e':
            x = x + 1
        elif move == 's':
            y = y + 1
        elif move == 'w':
            x = x - 1

        if x > self.document['width'] - 1 or \
                x < 0 or \
                y < 0 or \
                y > self.document['height'] - 1:
            result['kill'] = True
        else:
            result['new_head'] = (x, y, player_id)
            player['queue'].append((x, y))

        player['last_move'] = move

        if player['ate_last_turn']:
            player['ate_last_turn'] = False
        else:
            # remove tail from player and game board
            tail = player['queue'].pop(0)
            result['tail'] = (tail[0], tail[1], player_id)

        return result

    def player_kill(self, player):
        print 'killing player: %s' % player['name']

        for position in player['queue']:
            self.board_remove_piece(position, player['id'])
        player['status'] = 'dead'

    def game_get_player_moves(self):
        snapshot = self.document['state'].copy()

        def get_player_move(player, snapshot):
            path = 'tick/%s' % player['id']
            data = self._client_request(player, path, snapshot)
            result = {
                'player_id': player['id'],
                'data': data,
            }
            return result

        moves = []
        for player in self.document['players']:
            if player['url'] != settings.LOCAL_PLAYER_URL:
                moves.append(gevent.spawn(get_player_move, player, snapshot))

        return moves

    def game_calculate_collisions(self, x, y):
        square = self.document['state']['board'][y][x]
        to_kill = []

        if len(square) == 2:
            first = square[0]
            second = square[1]

            if first['type'] == settings.FOOD or second['type'] == settings.FOOD:
                # snake food collision
                if first['type'] == settings.FOOD:
                    self._give_food(second['id'])
                    square.remove(first)
                else:
                    self._give_food(first['id'])
                    square.remove(second)

            else:
                for thing in square:
                    # kill all the non food
                    if thing['type'] == settings.SNAKE_HEAD:
                        to_kill.append(thing['id'])
                    elif thing['type'] == settings.SNAKE:
                        self._give_kill(thing['id'])

        elif len(square) > 2:
            for thing in square:
                # kill all the non food
                if thing['type'] == settings.SNAKE_HEAD:
                    to_kill.append(thing['id'])
                elif thing['type'] == settings.SNAKE:
                    self._give_kill(thing['id'])

        return to_kill

    def game_calculate_highscore(self):
        highscores = Highscores(self.db)
        highscores.update(self.document)

    def tick(self, local_player_move=None):
        self.board_maybe_add_food()

        to_kill = []
        tails = []
        new_heads = []
        old_heads = []

        moves = self.game_get_player_moves()

        ## MOVE LOCAL PLAYER
        if local_player_move:
            # Simulate regular move response
            moves.append({
                'local_move': local_player_move
            })

        for move in moves:
            if 'local_move' in move:
                move = move['local_move']
            else:
                move = move.value

            player_id = move['player_id']
            player = self._get_snake(player_id)

            if player['status'] == 'dead':
                # make sure the playre isnt dead
                continue

            data = move['data']

            ## SET PLAYER MESSAGE
            if 'message' in data:
                player['message'] = data['message']
            else:
                player['message'] = ''

            player_move = self.player_compute_move(player, data['move'])

            if player_move['kill']:
                to_kill.append(player)

            if player_move['tail']:
                tails.append(player_move['tail'])

            if 'new_head' in player_move:
                # only if the player has a new head do we add it
                # and remove the old one
                new_heads.append(player_move['new_head'])
                old_heads.append(player_move['old_head'])

        # set the old player head as just snake
        for head in old_heads:
            self.board_remove_piece((head[0], head[1]), head[2])
            self.board_place_snake((head[0], head[1]), head[2])

        # first lets go through and add all the new heads
        for head in new_heads:
            self.board_place_snake_head((head[0], head[1]), head[2])

        # now lets go back through and do collisions
        for head in new_heads:
            x = head[0]
            y = head[1]

            # try and calculate collisions
            new_kills = self.game_calculate_collisions(x, y)

            # update the kills
            to_kill.extend(new_kills)

        # Remove old tails
        for tail in tails:
            pos = (tail[0], tail[1])
            self.board_remove_piece(pos, tail[2])

        # 2: kill collisions
        alive_players = []
        for player in self.document['state']['snakes']:
            if player['id'] in to_kill and not player['status'] == 'dead':
                to_kill.remove(player['id'])
                self.player_kill(player)
            elif player['status'] == 'alive':
                alive_players.append(player)

        # GAME OVER!
        if len(alive_players) == 0:
            self.document['state']['game_over'] = True
            #self.game_calculate_highscore()

        self.document['state']['turn_num'] = int(self.document['state']['turn_num']) + 1

        self.save()

    def get_state(self):
        return self.document['state']
