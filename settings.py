
# static settings

import os

STATIC_FILES_DIR = 'static'

## MONGOHQ_URL should be mongodb://heroku:364c9b68ffdfa31560f41f5e0d6b53de@dharma.mongohq.com:10058/app16889606

# Defaults to localhost
MONGODB_URL = os.environ.get('MONGOHQ_URL', None)

LOCAL_PLAYER_URL = 'local_player'
SNAKE_HEAD = 'snake_head'
SNAKE = 'snake'
FOOD = 'food'
FOOD_CHANCE = 0

if MONGODB_URL:
    MONGODB_DATABASE = MONGODB_URL.split('/')[-1]
else:
    MONGODB_DATABASE = 'snakewithus'
