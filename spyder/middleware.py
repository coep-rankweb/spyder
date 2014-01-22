from scrapy import log
from urlparse import urlparse
from scrapy.exceptions import IgnoreRequest
import sys
sys.path.append("../")
from datastore import Datastore

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
		if response.headers['Content-Type'] not in ['text/html', 'text/plain']:
			log.msg(vars(request), level=log.WARNING)
			raise IgnoreRequest
		return response

		
