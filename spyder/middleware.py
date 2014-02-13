from scrapy import log
from urlparse import urlparse
from scrapy.exceptions import IgnoreRequest
from scrapy.selector import Selector
import sys
sys.path.append("../")
from datastore import Datastore
import langid
import base64

class RequestsLimiter(object):
	def __init__(self):
		self.r = Datastore()
		#self.r.flushdb()
		self.DOMAIN = "DOMAIN"
		self.LIMIT = 200
		self.DOMAIN_SET = "DOMAIN_SET"

	def process_request(self, request, spider):
		domain = urlparse(request.url).hostname
		if int(self.r.get(self.DOMAIN + ":" + domain) or 0) < self.LIMIT:
			self.r.sadd(self.DOMAIN_SET, domain)
			self.r.incr(self.DOMAIN + ":" + domain, 1)
			return None
		else:
			log.msg(request.url, level=log.WARNING)
			raise IgnoreRequest

	def process_response(self, request, response, spider):
		try:

			if 'text/html' not in response.headers['Content-Type'] and 'text/plain' not in response.headers['Content-Type']:
				log.msg(vars(request), level=log.WARNING)
				raise IgnoreRequest

			if langid.classify(response.body)[0] != 'en':
				raise IgnoreRequest
		except KeyError:
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
