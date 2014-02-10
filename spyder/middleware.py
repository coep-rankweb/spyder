from scrapy import log
from urlparse import urlparse
from scrapy.exceptions import IgnoreRequest
from scrapy.selector import Selector
import sys, os
sys.path.extend(["../", "spyder/"])
from pymongo import MongoClient
from defines import *
import langid
import base64
import traceback
from timer import timeit

class RequestsLimiter(object):
	def __init__(self):
		self.r = MongoClient(os.environ.get("MONGOHQ_URL"))
		self.db = self.r[DB_NAME]
		self.d = self.db[DOMAIN_DATA]

	def process_request(self, request, spider):
		domain = urlparse(request.url).hostname
		self.d.update({'domain': domain}, {"$inc": {"freq": 1}}, upsert = True)
		res = self.d.find_one({'domain': domain})
		if res['freq'] > DOMAIN_LIMIT:
			raise IgnoreRequest
		else:
			return None

	def process_response(self, request, response, spider):
		try:
			if 'text/html' not in response.headers['Content-Type'] and 'text/plain' not in response.headers['Content-Type']:
				raise IgnoreRequest

			if langid.classify(response.body)[0] != 'en':
				raise IgnoreRequest
		except KeyError:
			raise IgnoreRequest

		return response
