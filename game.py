import json
import requests
from random import randint
from uuid import uuid4

from pymongo import MongoClient

import settings


def get_mongodb():
    client = MongoClient(host=settings.MONGODB_URL)
    return client[settings.MONGODB_DATABASE]


class Game(object):

    document = None
    _MONGODB_COLLECTION_NAME = 'snakewithus'

    def __init__(self, game_id=None, player_urls=None, local_player=None,
            width=None, height=None):
        self._mongodb = get_mongodb()
        db = self._get_mongo_collection()

        self.created = False
        self.game_id = game_id

        if not self.game_id:
            self.game_id = self._gen_id()
            self.created = True

            # first setup our players
            players = []

            if not player_urls:
                player_urls = []

            for url in player_urls:
                player = {
                    'url': url,
                    'id': self._gen_id(),
                    'queue': [self._gen_start_position(width, height)]
                }

                players.append(player)

            # next setup inital game state
            state = {
                'id': self.game_id,
                'board': self._gen_initial_board(players, width, height),
                'snakes': self._gen_snakes(players),
                'turn_num': 0
            }

            self.document = db.insert({
                'id': self.game_id,
                'players': players,
                'local_player': local_player,
                'state': state,
                'width': width,
                'height': height
            })
        else:
            self.document = self._fetch_game()

    def _gen_snakes(self, players=[]):
        # copy players
        snakes = list(players)
        for player in snakes:
            player['last_move'] = ''
            player['name'] = ''
            player['status'] = 'alive'
            player['message'] = ''
            player['points'] = {
                'kills': 0,
                'food': 0
            }
        return snakes

    def _gen_initial_board(self, players, width, height):
        board = []
        for x in range(0, width):
            board.append([])
            for y in range(0, height):
                board[x].append([])

        for player in players:
            start_pos = player[ 'queue' ][0]
            board[start_pos[0]][start_pos[1]].append({
                'type': 'head',
                'id': player['id']
            })
        return board

    def _gen_start_position(self, width, height):
        return randint(0, width), randint(0, height)

    def _gen_id(self):
        return uuid4().urn

    def _get_mongo_collection(self):
        return self._mongodb[self._MONGODB_COLLECTION_NAME]

    def _fetch_game(self):
        db = self._get_mongo_collection()
        search = db.find({'id': self.game['id']})
        if len(search) != 1:
            return None

        return search[0]

    def save(self):
        """saves game to mongo"""
        db = self._get_mongo_collection()
        db.save(self.document)

    def resolve_food(self):
        pass

    def apply_player_move(self, player, move):
        coords = player[ 'queue' ][-1]  # head
        x = coords[0]
        y = coords[1]

        # snake moves forward, change snake_head to snake
        board = self.document['state']['board']
        for obj in board[x][y]:
            if obj['id'] == player['id']:
                obj['type'] = 'snake'

        # update player queue and board state with new head
        if move == 'n':
            if player['last_move'] == 's':
                return True
            y = y + 1
        elif move == 'e':
            if player['last_move'] == 'w':
                return True
            x = x + 1
        elif move == 's':
            if player['last_move'] == 'n':
                return True
            y = y - 1
        elif move == 'w':
            if player['last_move'] == 'e':
                return True
            x = x - 1

        player[ 'queue' ].append((x, y))
        board[x][y].append({'type': 'snake_head', 'id': player['id']})

        # remove tail from player and game board
        tail = player[ 'queue' ].pop(0)
        square = board[tail[0]][tail[1]]
        for obj in square:
            if obj['id'] == player['id']:
                square.remove(obj)

        if x > self.document['width'] or x < 0 or y < 0 or y > self.document['height']:
            return True
        return False

    def _give_food(self, snake_id):
        # give food to this snake
        for snake in self.document['state']['snakes']:
            if snake['id'] == snake_id:
                snake.stats.food += 1
                return

    def _give_kill(self, snake_id):
        # give kills to this snake
        for snake in self.document['state']['snakes']:
            if snake['id'] == snake_id:
                snake.stats.kills += 1
                return

    def _set_snake_message(self, snake_id, message):
        for snake in self.document['state']['snakes']:
            if snake['id'] == snake_id:
                snake.messages = message
                return

    def tick(self):
        snapshot = self.document['state'].copy()

        to_kill = []
        for player in self.document['players']:
            response = requests.post(player['url'], data=json.dumps(snapshot))
            self._set_snake_message(player['id'], response.json().message)
            should_kill = self.apply_player_move(player, response.json().move)

            if should_kill:
                to_kill.append(player['id'])

        # 1: find collisions
        for x in range(0, len(self.document['width'])):
            for y in range(0, len(self.document['height'])):
                square = self.document['state']['board'][x][y]

                if len(square) == 2:
                    first = square[0]
                    second = square[1]

                    if first['type'] == 'food' or second['type'] == 'food':
                        # snake food collision
                        if first['type'] == 'food':
                            self._give_food(second['id'])
                        else:
                            self._give_food(first['id'])
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
                        if thing.type == 'snake_head':
                            to_kill.append(thing['id'])
                        elif thing.type == 'snake':
                            self._give_kill(thing['id'])

        # 2: kill collisions
        for snake in self.document['state']['snakes']:
            if snake['id'] in to_kill:
                snake['status'] = 'dead'

                for player in self.document['players']:
                    if player['id'] == snake['id']:
                        for position in player['queue']:
                            x = position[0]
                            y = position[1]
                            square = self.document['state']['board'][x][y]
                            for thing in square:
                                if thing['id'] == snake['id']:
                                    square.remove(thing)
                                    break
                        break

    def get_state(self):
        return self.document['state']
