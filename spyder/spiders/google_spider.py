from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from spyder.items import WebItem
from unidecode import unidecode
from scrapy import log
from urlparse import urljoin

class GoogleSpider(CrawlSpider):
	name = "google"
	allowed_domains = []

	#start_urls = ["http://www.nobelprize.org/nobel_prizes/physics/laureates/1921/einstein-bio.html"]
	#start_urls = ["http://en.wikipedia.org/wiki/Bill_Gates"]
	start_urls = ["http://www.moreintelligentlife.com/"]

	rules = (
		Rule(SgmlLinkExtractor(allow = (".*", )), callback = 'process', follow = True),
	)

	def process(self, response):
		sel = Selector(response)
		item = WebItem()
		name = sel.xpath("//title/text()").extract()
		if name:
			item['title'] = self.clean(name[0])
		else:
			item['title'] = ""
		item['url'] = response.url
		item['raw_html'] = response.body
		rel_links = sel.xpath('//a/@href').extract()
		meta = sel.xpath('//meta[@name="description"]/@content').extract()
		if meta: meta = meta[0]
		else: meta = ""
		item['meta_description'] = meta
		abs_links = []
		for l in rel_links:
			abs_links.append(urljoin(response.url, l))
		item['link_set'] = abs_links
		return item

	def clean(self, s):
		s = self.encode_str(s)
		s = s.strip()
		s = s.replace('\n', ' ').replace('|', '-').replace('\t', ' ')
		return s

	def encode_str(self, s):
		if type(s) == unicode:
			#return u''.join(s).encode('utf-8').strip()
			return unidecode(s)
		else:
			return unidecode(s.decode("utf-8", "ignore"))

