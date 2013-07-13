import requests

from uuid import uuid4

from pymongo import MongoClient

import settings

def get_mongodb():
	client = MongoClient(host=settings.MONGODB_URL)
	return client[settings.MONGODB_DATABASE]

class Game(object):

    document = None
    _MONGODB_COLLECTION_NAME = 'snakewithus'

    def __init__(self, game_id=None, player_urls=None, local_player=None):
        self._mongodb = get_mongodb()
        db = self._get_mongo_collection()

        self.created = False
        self.game_id = game_id

        if not self.game_id:
            self.game_id = uuid4().urn
            self.created = True

            document = db.insert({
                id: self.game_id,
                player_urls: player_urls,
                local_player:local_player
            })
        else:
            self.document = self._fetch_game()

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
        for url in self.document.player_urls:
            response = requests.post()
