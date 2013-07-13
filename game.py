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

            document = db.insert({
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
            player['facing'] = ''
            player['status'] = 'alive'
            player['message'] = ''
            player['points'] = {
                'kills': 0,
                'food': 0
            }
        return snakes

    def _gen_initial_board(self, players, width, height):
        board = []
        for x in range(0, 100):
            board[x] = []
            for y in range(0, 100):
                board[x].append([])

        for player in players:
            start_pos = player.queue[0]
            board[start_pos[0]][start_pos[1]].append({
                'type': 'head',
                'id': player.id
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
        search = db.find({id: self.game_id})
        if len(search) != 1:
            return None

        self.document = search[0]

    def save(self):
        """saves game to mongo"""
        db = self._get_mongo_collection()
        db.save(self.document)

    def resolve_food(self):
        pass

    def apply_player_move(self, player, move):
        coords = player.queue[-1]  # head
        x = coords[0]
        y = coords[1]

        if move == 'n':
            player.queue.append((x, y + 1))
        elif move == 'e':
            player.queue.append((x + 1, y))
        elif move == 's':
            player.queue.append((x, y - 1))
        elif move == 'w':
            player.queue.append((x - 1, y))

        player.queue.pop(0)  # remove the tail

    def tick(self):
        snapshot = self.document.state.copy()

        for player in self.document.players:
            response = requests.post(player.url)
            self.apply_player_move(player, response.json().move)
