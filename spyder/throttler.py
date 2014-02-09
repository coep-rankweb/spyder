from __future__ import print_function
import sys, os
import time
sys.path.append(os.path.abspath('../'))
from defines import *
from datastore import Datastore

def throttle(method):
	def wrapper(class_obj, item, *args, **kwargs):
		if item['shutdown']:
			return item
		return method(class_obj, item, *args, **kwargs)
	return wrapper

def final_throttle(method):
	def wrapper(class_obj, item, *args, **kwargs):
		if item['shutdown']:
			Datastore().update(CRAWLER_DATA, {'spider': 'google'}, {'POWER_SWITCH': 'kill'})
			return item
		return method(class_obj, item, *args, **kwargs)
	return wrapper
