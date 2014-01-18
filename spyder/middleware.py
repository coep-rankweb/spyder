from scrapy import log
from urlparse import urlparse
from scrapy.exceptions import IgnoreRequest
import redis

class RequestsLimiter(object):
	def __init__(self):
		self.r = redis.Redis()
		#self.r.flushdb()
		self.DOMAIN = "DOMAIN_"
		self.LIMIT = 200
		self.DOMAIN_SET = "DOMAINSET"

	def process_request(self, request, spider):
		domain = urlparse(request.url).hostname
		if int(self.r.get(self.DOMAIN + domain) or 0) < self.LIMIT:
			self.r.sadd(self.DOMAIN_SET, domain)
			self.r.incr(self.DOMAIN + domain, 1)
			return None
		else:
			log.msg(request.url, level=log.WARNING)
			raise IgnoreRequest

		
