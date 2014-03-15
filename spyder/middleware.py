from scrapy import log
from urlparse import urlparse
from scrapy.exceptions import IgnoreRequest
from scrapy.selector import Selector
import sys
sys.path.append("../")
from datastore import Datastore
#import langid
import base64

class RequestsLimiter(object):
	def __init__(self):
		self.remote_r = Datastore("10.1.99.15")
		self.DOMAIN = "DOMAIN"
		self.LIMIT = 200
		self.DOMAIN_SET = "DOMAIN_SET"
		self.MAX_URL_LENGTH = 512

	def process_request(self, request, spider):
		try:
			if len(request.url) > self.MAX_URL_LENGTH: raise IgnoreRequest
			domain = urlparse(request.url).hostname
			if int(self.remote_r.get(self.DOMAIN + ":" + domain) or 0) < self.LIMIT:
				self.remote_r.sadd(self.DOMAIN_SET, domain)
				self.remote_r.incr(self.DOMAIN + ":" + domain, 1)
				return None
			else:
				log.msg("DOMAIN limit Crossed:%s" % request.url, level=log.CRITICAL)
				raise IgnoreRequest
		except TypeError as e:
			raise IgnoreRequest


	def process_response(self, request, response, spider):
		try:
			if response.status != 200: raise IgnoreRequest
			if 'text/html' not in response.headers['Content-Type'] and 'text/plain' not in response.headers['Content-Type']:
				log.msg("Non-HTML/Plain:%s" % request.url, level=log.CRITICAL)
				raise IgnoreRequest

			'''
			if langid.classify(response.body)[0] != 'en':
				log.msg("Non-English:%s" % request.url, level=log.CRITICAL)
				raise IgnoreRequest
			'''

		except KeyError:
			log.msg("KeyError(Content-Type):%s" % request.url, level=log.CRITICAL)
			raise IgnoreRequest

		del request
		return response
'''
class ProxyMiddleware(object):
	def process_request(self, request, spider):
		request.meta['proxy'] = "http://10.1.101.150:3128"
		proxy_user_pass = "111301014:Test_123"
		encoded_user_pass = base64.encodestring(proxy_user_pass)
		request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
'''
