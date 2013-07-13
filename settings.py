
# static settings

import os

STATIC_FILES_DIR = 'static'

MONGODB_URL = os.environ.get('MONGOHQ_URL', 'mongodb://heroku:364c9b68ffdfa31560f41f5e0d6b53de@dharma.mongohq.com:10058/app16889606')
MONGODB_DATABASE = MONGODB_URL.split('/')[-1]
