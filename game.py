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

    def _create_game(self, local_player, width, height):
        self.game_id = generate_game_id()
        self.created = True

        # next setup inital game state
        state = {
            'id': self.game_id,  # Should this be in here too?
            'snakes': [],
            'board': self._gen_initial_board(width, height),
            'turn_num': 0
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

    def _gen_snake_and_player(self, player_url, width, height):
        id = self._gen_id()

        # keep player url private
        player = {
            'url': player_url,
            'id': id,
        }

        # public player
        snake = {
            'id': id,
            'queue': [self._gen_start_position(width, height)]
        }
        snake['ate_last_turn'] = False
        snake['last_move'] = ''
        snake['name'] = ''
        snake['status'] = 'alive'
        snake['message'] = ''
        snake['points'] = {
            'kills': 0,
            'food': 0
        }

        return snake, player

    def _gen_initial_board(self, width, height):
        board = []

        ## BUILD EMPTY BOARD
        for x in range(0, width):
            board.append([])
            for y in range(0, height):
                board[x].append([])

        return board

    def _add_snake_to_board(self, snake):
        board = self.document['state']['board']
        start_pos = snake['queue'][0]
        x = start_pos[0]
        y = start_pos[1]

        board[x][y].append({
            'type': 'snake_head',
            'id': snake['id']
        })

        self.document['state']['board'] = board

    def _gen_start_position(self, width, height):
        return (randint(0, width-1), randint(0, height-1))

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
                return self.document

        ## CREATE NEW PLAYER AND SNAKE
        new_snake, new_player = self._gen_snake_and_player(
            player_url,
            self.document['width'],
            self.document['height']
        )

        ## ADD SNAKE TO BOARD
        self._add_snake_to_board(new_snake)

        ## UPDATE DOC
        self.document['players'].append(new_player)
        self.document['state']['snakes'].append(new_snake)

        self.save()

        return new_player

    def do_client_register(self):
        """Registers all the clients asynchronously"""
        def client_register(player):
            data = {
                'game_id': self.game_id,
                'client_id': player['id'],
                'board': {
                    'width': self.document['width'],
                    'height': self.document['height'],
                    'num_players': len(self.document['state']['snakes'])
                }
            }

            response = {
                'data': self._client_request(player, 'register', data),
                'player_id': player['id']
            }

            return response

        events = [gevent.spawn(client_register, player) for player in self.document['players']]
        gevent.joinall(events)

        for event in events:
            player = self._get_snake(event.value['player_id'])
            player['name'] = event.value['data']['name']

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
        snake['stats']['food'] += 1

    def _give_kill(self, snake_id):
        # give kills to this snake
        snake = self._get_snake(snake_id)
        snake['stats']['kills'] += 1

    def apply_player_move(self, player, move):
        coords = player['queue'][-1]  # head
        x = coords[0]
        y = coords[1]

        old_x = x
        old_y = y

        # snake moves forward, change snake_head to snake
        board = self.document['state']['board']
        for obj in board[x][y]:
            if obj['id'] == player['id']:
                obj['type'] = 'snake'

        # update player queue and board state with new head
        if move == 'n':
            y = y + 1
        elif move == 'e':
            x = x + 1
        elif move == 's':
            y = y - 1
        elif move == 'w':
            x = x - 1

        print 'player moved: (%s,%s) -> (%s,%s)' % (old_x, old_y, x, y)

        if x > self.document['width'] - 1 or x < 0 or y < 0 or y > self.document['height'] - 1:
            return True

        player['queue'].append((x, y))
        board[x][y].append({'type': 'snake_head', 'id': player['id']})

        player['last_move'] = move

        if player['ate_last_turn']:
            player['ate_last_turn'] = False
        else:
            # remove tail from player and game board
            tail = player['queue'].pop(0)
            square = board[tail[0]][tail[1]]
            for obj in square:
                if obj['id'] == player['id']:
                    square.remove(obj)

        return False

    def player_remove_old_head(self, player, x, y):
        board = self.document['state']['board']
        for obj in board[x][y]:
            if obj['id'] == player['id']:
                obj['type'] = 'snake'
                return

    def player_add_new_head(self, player_id, x, y):
        self.document['state']['board'][x][y].append({'type': 'snake_head', 'id': player_id})

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
            y = y + 1
        elif move == 'e':
            x = x + 1
        elif move == 's':
            y = y - 1
        elif move == 'w':
            x = x - 1

        if x > self.document['width'] - 1 or x < 0 or y < 0 or y > self.document['height'] - 1:
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
            result['tail'] = tail

        return result

    def player_remove_square(self, player, x, y):
        square = self.document['state']['board'][x][y]
        for obj in square:
            if obj['id'] == player['id']:
                square.remove(obj)
                return

    def player_change_head(self, player_id, x, y):
        board = self.document['state']['board']
        for obj in board[x][y]:
            if obj['id'] == player_id:
                obj['type'] = 'snake'
                return

    def player_kill(self, player):
        print 'killing player: %s' % player['name']

        player['status'] = 'dead'

        for position in player['queue']:
            x = position[0]
            y = position[1]
            square = self.document['state']['board'][x][y]
            for thing in square:
                if thing['id'] == player['id']:
                    square.remove(thing)
                    break

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
        square = self.document['state']['board'][x][y]
        to_kill = []

        if len(square) == 2:
            first = square[0]
            second = square[1]

            if first['type'] == 'food' or second['type'] == 'food':
                # snake food collision
                if first['type'] == 'food':
                    self._give_food(second['id'])
                    square.remove(first)
                else:
                    self._give_food(first['id'])
                    square.remove(second)

            else:
                for thing in square:
                    # kill all the non food
                    if thing['type'] == 'snake_head':
                        to_kill.append(thing['id'])
                    elif thing['type'] == 'snake':
                        self._give_kill(thing['id'])
        elif len(square) > 2:
            for thing in square:
                # kill all the non food
                if thing['type'] == 'snake_head':
                    to_kill.append(thing['id'])
                elif thing['type'] == 'snake':
                    self._give_kill(thing['id'])

        return to_kill

    def tick(self, local_player_move=None):

        to_kill = []
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
                x = player_move['tail'][0]
                y = player_move['tail'][1]
                self.player_remove_square(player, x, y)

            if 'new_head' in player_move:
                print("HELLO %s" % player_move)
                # only if the player has a new head do we add it
                # and remove the old one
                new_heads.append(player_move['new_head'])
                old_heads.append(player_move['old_head'])

        # set the old player head as just snake
        for head in old_heads:
            self.player_change_head(head[2], head[0], head[1])

        # first lets go through and add all the new heads
        for head in new_heads:
            x = head[0]
            y = head[1]

            self.player_add_new_head(head[2], x, y)

        # now lets go back through and do collisions
        for head in new_heads:
            x = head[0]
            y = head[1]
            # try and calculate collisions
            new_kills = self.game_calculate_collisions(x, y)

            # update the kills
            to_kill = to_kill + new_kills

        # 2: kill collisions
        for player in self.document['state']['snakes']:
            if player['id'] in to_kill and not player['status'] == 'dead':
                to_kill.remove(player['id'])
                self.player_kill(player)

        self.document['state']['turn_num'] = int(self.document['state']['turn_num']) + 1

    def get_state(self):
        return self.document['state']
