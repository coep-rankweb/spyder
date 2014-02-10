from __future__ import print_function
import sys, os
import time
sys.path.append(os.path.abspath('../'))
from defines import *
from pymongo import MongoClient
from urlparse import urlparse


def throttle(method):
	def wrapper(class_obj, item, *args, **kwargs):
		if item['shutdown']:
			return item
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
			c.update({"spider": "google"}, {"$set": {"POWER_SWITCH": "KILL"}})
			return item
		return method(class_obj, item, *args, **kwargs)
	return wrapper
