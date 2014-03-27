from scrapy import log
import os
import sys
sys.path.append(os.path.abspath('../'))
from defines import *
from scrapy.exceptions import DropItem
import nltk
from unidecode import unidecode
from throttler import throttle, final_throttle, first_throttle
import itertools
from timer import timeit
from pymongo import MongoClient
from urlparse import urlparse
import redis

from bs4 import BeautifulSoup
import re
from unidecode import unidecode

MU = os.environ.get("MONGOHQ_URL")
r = MongoClient(MU)
if MU: db = r[urlparse(MU).path[1:]]
else: db = r[DB_NAME]
u = db[URL_DATA]
w = db[WORD_DATA]
c = db[CRAWLER_DATA]
arch_u = db[ARCHIVE_URL_DATA]
arch_w = db[ARCHIVE_WORD_DATA]

red = redis.Redis()
#co = db[COLLOCATIONS_DATA]
#f = db[FREQ_DATA]

u.create_index('url')
w.create_index('word')
arch_u.create_index('url')
arch_w.create_index('word')
#co.create_index('base')

class Gatekeeper(object):
	'''
	Filters duplicate urls
	Assigns each url a unique id
	Sets url -> id and id -> url in redis
	Indexes inlinks and outlinks
	'''
	def __init__(self):
		self.URL_CTR = itertools.count(1)
		self.flag = False

	@first_throttle
	def process_item(self, item, spider):
		self.buildURLIndex(item)
		return item

	def buildURLIndex(self, item):
		'''
		Assign id to current url
		Each link's url is assigned an ID and vice versa
		'''
		#url has not been processed before (or has been assigned an id via an outlink; so check for that first!)
		new_url_id = -1
		url_obj = u.find_one({'url': item['url']})
		if not url_obj:
			# no id assigned, never seen this url before
			url_id = self.URL_CTR.next()
			u.insert({'_id': url_id, 'url': item['url'], 'title': item['title']})
			arch_u.insert({'_id': url_id, 'url': item['url'], 'title': item['title']})
		elif url_obj.has_key('title'):
			# url has been processed and assigned a title
			url_id = url_obj['_id']
		else:
			# url has been assigned an id as an outlink of some processed page
			url_id = url_obj['_id']
			u.update(url_obj, {'$set': {'title': item['title']}})
			arch_u.update(url_obj, {'$set': {'title': item['title']}})
			
		item['url_id'] = url_id

		out_links = set()
		for link in item['link_set']:
			res = u.find_one({'url': link})
			if not res:
				new_url_id = self.URL_CTR.next()
				u.insert({'_id': new_url_id, 'url': link})
				arch_u.insert({'_id': new_url_id, 'url': link})
			else:
				new_url_id = res['_id']
			out_links.add(new_url_id)
		u.update({'_id': url_id}, {"$set": {"out_links": list(out_links)}})
		arch_u.update({'_id': url_id}, {"$set": {"out_links": list(out_links)}})

class TextExtractor(object):
	''' Extracts text from the raw_html field of the item '''
	def __init__(self):
		self.flag = False


	def clean(self, b):
		try: b = unicode(b, "UTF-8")
		except: pass
		b = unidecode(b)
		soup = BeautifulSoup(b)
		to_remove = soup.find_all(class_ = re.compile(".*comment.*"))
		s = str(soup)
		for rem in to_remove:
			s = s.replace(str(rem), " ")
		return s


	@throttle
	def process_item(self, item, spider):
		if not item['raw_html']:
			item['extracted_text'] = ""
		else:
			item['extracted_text'] = nltk.clean_html(self.clean(item['raw_html']))
		return item


class KeywordExtractor(object):
	'''
	Extracts keywords from title, extracted_text, meta_description
	'''
	def __init__(self):
		self.WORD_CTR = itertools.count(1)
		self.flag = False
		self.score = { 'url':10, 'title':10, 'body':1 }
		self.stopwords = set(['all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should', 'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did', 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 'out', 'what', 'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about', 'of', 'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too', 'themselves', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself', 'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have', 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after', 'most', 'such', 'why', 'a', 'off', 'i', 'yours', 'so', 'the', 'having', 'once'])


	def tokenize(self, text):
		d = {}
		words = nltk.wordpunct_tokenize(text)
		cleaned_words = [self.clean(w) for w in words if w.isalnum() and len(w) > 1 and not w.isdigit()]
		for word in cleaned_words:
			if word not in self.stopwords:
				try: d[word] += 1
				except KeyError: d[word] = 1
		return d

	@final_throttle
	def process_item(self, item, spider):
		p = urlparse(item['url'])
		host = p.hostname.replace("www.", " ").replace(".com", " ")
		path = p.path.replace(".html", " ").replace(".htm", " ")

		d_url = self.tokenize(host + " " + path)
		d_title = self.tokenize(item['title'])
		d_body = self.tokenize(item['extracted_text'])

		url_list = self.buildWordIndex(item, d_url, "url")
		title_list = self.buildWordIndex(item, d_title, "title")
		body_list = self.buildWordIndex(item, d_body, "body")

		d = {}
		for word_dict in url_list:
			d[word_dict['word']] = d.get(word_dict['word'], 0) + word_dict['freq']

		for word_dict in title_list:
			d[word_dict['word']] = d.get(word_dict['word'], 0) + word_dict['freq']

		for word_dict in body_list:
			d[word_dict['word']] = d.get(word_dict['word'], 0) + word_dict['freq']

		word_list = [ {'word':i, 'score':d[i]} for i in d ]

		for i in word_list:
			w.update({'_id': i['word']}, {"$addToSet": {'present_in': {"url": item['url_id'], "score": i['score']}}})

		u.update({'_id': item['url_id']}, {"$set": {"word_vec": word_list}})
		c.update({'spider': 'google'}, {"$inc": {'url_count': 1}})
		red.incr("processed_ctr", 1)

		print item['url']
		sys.stderr.write("%s\t:\t%s\n" % (item['url_id'], item['url']))
		return item

	def buildWordIndex(self, item, text_dict, pos):
		'''
		Get current url id
		For each word in current url's text,
			add the url to the set of urls which contain that word

		'''
		url_id = item['url_id']
		word_id = -1
		key = "in_%s" % pos
		word_list = []
		url_list = []

		for word in text_dict:
			res = w.find_one({'word': word})
			if res:
				word_id = res['_id']
			else:
				word_id = self.WORD_CTR.next()
				w.insert({'word': word, '_id': word_id})
				arch_w.insert({'word': word, '_id': word_id})
				c.update({'spider': 'google'}, {"$inc": {'word_count': 1}})

			word_list.append({ "word": word_id, "freq": text_dict[word] * self.score[pos] })

			arch_w.update({'_id': word_id}, {"$addToSet": {key: {"url": url_id, "freq": text_dict[word]}}})

		arch_u.update({'_id': url_id}, {"$set": {"word_vec": word_list}})

		return word_list

	def clean(self, s):
		return s.lower()
