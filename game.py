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
                    queue: [self._gen_start_position(width, height)]
                }

                players.append(player)

            # next setup inital game state
            state = {
                'id': self.game_id,
                'board': self._gen_initial_board(players),
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

    def _gen_initial_board(self, players=[]):
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

    def tick(self):

        snapshot = self.document.state.copy()

        def apply_player_move(direction):
            # update snapshot board object to reflect move
            pass

        # post to each client to obtain move
        for player in self.document.players:
            response = requests.post(url)
            # get dir and pass to apply_player_move

        # resolve collisions / food



        # update mongo store



