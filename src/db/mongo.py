'''
Provides a database connection `con` to wikilytics.
'''

import settings
import pymongo


mongodb = None
'''Name of the mongo database
'''
if 'mongodb' in settings.__dict__:
    mongodb = settings.mongodb
else:
    mongodb = 'wikilytics'



mongocol = None
'''Name of the mongo collection
'''
if 'mongocol' in settings.__dict__:
    mongocol = settings.mongocol
else:
    mongocol = 'enwiki_editors_dataset'



con = None
'''Connection instance to the mongo db
'''
db = None
col = None

def connect():
  con = pymongo.Connection(slave_okay=True)
  db = con[mongodb]
  col = db[mongocol]
  