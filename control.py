import sys, os
from pymongo import MongoClient
sys.path.extend(["../", "spyder/"])
from defines import *
from urlparse import urlparse
import redis

MU = os.environ.get("MONGOHQ_URL")
r = MongoClient(MU)
if MU: db = r[urlparse(MU).path[1:]]
else: db = r[DB_NAME]
red = redis.Redis()

def reset():
	red.flushdb()
	for collection in db.collection_names():
		if collection in [URL_DATA, PROC_URL_DATA, WORD_DATA, PROC_WORD_DATA, CRAWLER_DATA, COLLOCATIONS_DATA, FREQ_DATA, DOMAIN_DATA]:
			db.drop_collection(collection)

def init():
	c = db[CRAWLER_DATA]
	c.insert({"spider": "google", "url_count": 0, "word_count": 0})
	red.set("processed_ctr", 0)

def on():
	c = db[CRAWLER_DATA]
	c.update({"spider": "google"}, {"$set": {"POWER_SWITCH": "ON"}})
	red.set("POWER_SWITCH", "ON")

def off():
	c = db[CRAWLER_DATA]
	c.update({"spider": "google"}, {"$set": {"POWER_SWITCH": "OFF"}})
	red.set("POWER_SWITCH", "OFF")
