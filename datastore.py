from pymongo import MongoClient
import os

class Datastore:
	def __init__(self):
		mongourl = os.environ.get('MONGOLAB_URI')
		self.client = MongoClient(mongourl)
		self.DATABASE = "SPIDER_DB"
		self.db = self.client[self.DATABASE]

	def find_one(self, collection, *args, **kwargs):
		return self.db[collection].find_one(*args, **kwargs)

	def find(self, collection, spec = None, fields = None):
		return self.db[collection].find(spec, fields)

	def insert(self, collection, a):
		return self.db[collection].insert(a)

	def remove(self, collection, a):
		return self.db[collection].remove(a)

	def update(self, collection, query, update, upsert = True):
		return self.db[collection].update(query, update, upsert)

	def distinct(self, collection, a):
		return self.db[collection].distinct(a)

	def flushdb(self):
		return self.client.drop_database(self.db)
