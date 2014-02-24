from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from spyder.items import WebItem
from scrapy.exceptions import CloseSpider
from unidecode import unidecode
from scrapy import log
from urlparse import urljoin, urlparse
import sys
sys.path.append("../")
from datastore import Datastore
import traceback

class GoogleSpider(CrawlSpider):
	name = "google"
	allowed_domains = []

	start_urls = ["http://www.historylearningsite.co.uk/index.htm", "http://www.forbes.com/economics-finance/", "http://www.mit.edu/", "http://www.smithsonianmag.com/", "http://edition.cnn.com/", "http://www.engadget.com/", "http://www.amazon.com/", "http://espn.go.com/", "http://www.tlc.com/"] 
	rules = (
		Rule(SgmlLinkExtractor(allow = (".*", )), callback = 'process', follow = True),
	)
	r = Datastore()

	def process(self, response):
		status = self.r.get("POWER_SWITCH")
		item = WebItem()
		if status == "KILL":
			raise CloseSpider("shutdown")
		elif status == 'ON':
			try:
				sel = Selector(response)

				item['shutdown'] = False

				name = sel.xpath("//title/text()").extract()
				if name: item['title'] = self.clean(name[0])
				else: item['title'] = ""

				item['url'] = response.url
				item['raw_html'] = response.body

				meta = sel.xpath('//meta[@name="description"]/@content').extract()
				if meta: meta = self.clean(meta[0])
				else: meta = ""
				item['meta_description'] = meta

				abs_links = set()
				rel_links = sel.xpath('//a/@href').extract()
				for l in rel_links:
					link = urljoin(response.url, l)
					if urlparse(link).scheme in ['http', 'https']:
						abs_links.add(self.clean(link))
				item['link_set'] = abs_links

				return item
			except Exception as e:
				print e, response.url
				return None
		elif status == "OFF":
			item['shutdown'] = True
			return item
		else:
			raise CloseSpider("Invalid power switch value")

	def clean(self, s):
		s = self.encode_str(s)
		s = s.strip()
		s = s.replace('\n', ' ').replace('|', ' - ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
		return s

	def encode_str(self, s):
		temp = s
		try:
			temp = unicode(temp, encoding = "UTF-8")
		except:
			pass
		return unidecode(temp)
