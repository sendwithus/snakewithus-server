
# static settings

import os

STATIC_FILES_DIR = 'static'

MONGODB_URL = os.environ.get('MONGOHQ_URL', 'mongodb://localhost:27017/snakewithus')
MONGODB_DATABASE = MONGODB_URL.split('/')[-1]
