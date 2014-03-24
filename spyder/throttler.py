from __future__ import print_function
import sys, os
import time
sys.path.append(os.path.abspath('../'))
from defines import *
from pymongo import MongoClient
from urlparse import urlparse
import redis


def first_throttle(method):
	def wrapper(class_obj, item, *args, **kwargs):
		red = redis.Redis()
		if int(red.get("processed_ctr")) > 100000: item['shutdown'] = True
		if item['shutdown']: class_obj.flag = True
		if class_obj.flag: return item
		return method(class_obj, item, *args, **kwargs)
	return wrapper

def throttle(method):
	def wrapper(class_obj, item, *args, **kwargs):
		if item['shutdown']:
			class_obj.flag = True
			return item
		if class_obj.flag: return item
		return method(class_obj, item, *args, **kwargs)
	return wrapper

def final_throttle(method):
	def wrapper(class_obj, item, *args, **kwargs):
		if item['shutdown']:
			MU = os.environ.get("MONGOHQ_URL")
			r = MongoClient(MU)
			if MU: db = r[urlparse(MU).path[1:]]
			else: db = r[DB_NAME]
			c = db[CRAWLER_DATA]
			red = redis.Redis()
			red.set("POWER_SWITCH", "KILL")
			#c.update({"spider": "google"}, {"$set": {"POWER_SWITCH": "KILL"}})
			return item
		return method(class_obj, item, *args, **kwargs)
	return wrapper
