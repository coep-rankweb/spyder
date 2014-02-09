from scrapy import log
from urlparse import urlparse
from scrapy.exceptions import IgnoreRequest
from scrapy.selector import Selector
import sys
sys.path.extend(["../", "spyder/"])
from datastore import Datastore
from defines import *
#import langid
import base64
import traceback

class RequestsLimiter(object):
	def __init__(self):
		self.r = Datastore()

	def process_request(self, request, spider):
		domain = urlparse(request.url).hostname
		self.r.update(DOMAIN_DATA, {'domain': domain}, {"$inc": {"freq": 1}})
		res = self.r.find_one(DOMAIN_DATA, {'domain': domain})
		print res
		if res['freq'] > DOMAIN_LIMIT:
			raise IgnoreRequest
		else:
			return None

	def process_response(self, request, response, spider):
		if 'text/html' not in response.headers['Content-Type'] and 'text/plain' not in response.headers['Content-Type']:
			raise IgnoreRequest

		#if langid.classify(response.body)[0] != 'en':
		#	raise IgnoreRequest

		return response

class ProxyMiddleware(object):
	def process_request(self, request, spider):
		request.meta['proxy'] = "http://10.1.101.150:3128"
		proxy_user_pass = "111301014:Test_123"
		encoded_user_pass = base64.encodestring(proxy_user_pass)
		request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
