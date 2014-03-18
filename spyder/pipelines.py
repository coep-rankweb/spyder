from scrapy import log
import os
import sys
sys.path.append(os.path.abspath('../'))
from defines import *
from scrapy.exceptions import DropItem
import nltk
from unidecode import unidecode
from throttler import throttle, final_throttle
import itertools
from timer import timeit
from pymongo import MongoClient
from urlparse import urlparse

MU = os.environ.get("MONGOHQ_URL")
r = MongoClient(MU)
if MU: db = r[urlparse(MU).path[1:]]
else: db = r[DB_NAME]
u = db[URL_DATA]
w = db[WORD_DATA]
c = db[CRAWLER_DATA]
#co = db[COLLOCATIONS_DATA]
#f = db[FREQ_DATA]

u.create_index('url')
w.create_index('word')
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

	#@timeit("DuplicatesFilter")
	@throttle
	def process_item(self, item, spider):
		if c.find_one({'spider': 'google'})['processed_ctr'] > 200000:
			item['shutdown'] = True
		self.buildURLIndex(item)
		return item

	def buildURLIndex(self, item):
		'''
		Assign id to current url
		Each link's url is assigned an ID and vice versa
		'''
		#url has not been processed before
		new_url_id = -1
		url_id = self.URL_CTR.next()
		u.insert({'_id': url_id, 'url': item['url']})

		for link in item['link_set']:
			res = u.find_one({'url': link})
			if not res:
				new_url_id = self.URL_CTR.next()
				u.insert({'_id': new_url_id, 'url': link})
			else:
				new_url_id = res['_id']
			u.update({'_id': url_id}, {"$addToSet": {"out_links": new_url_id}})

class TextExtractor(object):
	''' Extracts text from the raw_html field of the item '''

	#@timeit("TextExtractor")
	@throttle
	def process_item(self, item, spider):
		if not item['raw_html']:
			item['extracted_text'] = ""
		else:
			temp = nltk.clean_html(item['raw_html'])
			try:
				temp = unicode(temp, encoding = "UTF-8")
			except TypeError:
				pass
			item['extracted_text'] = unidecode(temp)
		return item


class KeywordExtractor(object):
	'''
	Extracts keywords from title, extracted_text, meta_description
	'''
	def __init__(self):
		#self.r = Datastore()
		self.WORD_CTR = itertools.count(1)
		#self.stemmer = nltk.stem.PorterStemmer()
		self.stopwords = set(['all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should', 'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did', 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 'out', 'what', 'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about', 'of', 'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too', 'themselves', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself', 'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have', 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after', 'most', 'such', 'why', 'a', 'off', 'i', 'yours', 'so', 'the', 'having', 'once'])


	def tokenize(self, text):
		words = nltk.wordpunct_tokenize(text)
		cleaned_words = [self.clean(w) for w in words if w.isalnum() and len(w) > 1 and not w.isdigit()]
		return set(cleaned_words) - self.stopwords

	#@timeit("KeywordExtractor")
	@final_throttle
	def process_item(self, item, spider):
		url_words = self.tokenize(item['url'])
		title_words = self.tokenize(item['title'])
		body_words = self.tokenize(item['extracted_text'])

		self.buildWordIndex(item, url_words, "url")
		self.buildWordIndex(item, title_words, "title")
		self.buildWordIndex(item, body_words, "body")

		c.update({'spider': 'google'}, {"$inc": {'processed_ctr': 1}})

		try: sys.stderr.write("%s\n", str(item['url']))
		except: print "Couldnt write to file!", item['url']

		return item

	#@timeit("KeywordExtractor:buildWordIndex")
	def buildWordIndex(self, item, text, pos):
		'''
		Get current url id
		For each word in current url's text,
			add the url to the set of urls which contain that word
		'''
		url_id = u.find_one({"url": item['url']}, fields = ['_id'])['_id']
		word_id = -1
		key = "in_%s" % pos
		for word in text:
			#res = w.find_and_modify ({'word': word}, {"$setOnInsert": {"word": word, "_id":self.WORD_CTR.next()}}, upsert = True, full_response=True, new=True)
			res = w.find_one({'word': word})
			if res:
				word_id = res['_id']
			else:
				word_id = self.WORD_CTR.next()
				w.insert({'word': word, '_id': word_id})
			w.update({'_id': word_id}, {"$addToSet": {key: url_id}})
			u.update({'_id': url_id}, {"$addToSet": {"word_vec": word_id}})


	def clean(self, s):
		return s.lower()

class Analytics(object):
	'''
	Text analytics (if any)
	'''
	def __init__(self):
		#self.r = Datastore()
		self.TOP_N = 5
		self.bgm = nltk.collocations.BigramAssocMeasures
		self.SCORER_FN = self.bgm.likelihood_ratio

	#@timeit("Analytics")
	@final_throttle
	def process_item(self, item, spider):
		self.digram(item)
		self.freq(item)
		c.update({'spider': 'google'}, {"$inc": {'processed_ctr': 1}})
		print item['url']
		return item

	def digram(self, item):
		finder = nltk.collocations.BigramCollocationFinder.from_words(item['ordered_words'])
		digrams = finder.nbest(self.SCORER_FN, self.TOP_N)
		for digram in digrams:
			try:
				base_id = w.find_one({'word': digram[0]}, fields = ['_id'])['_id']
				next_id = w.find_one({'word': digram[1]}, fields = ['_id'])['_id']
				co.update({'base': base_id}, {"$inc": {'next.' + str(next_id): 1}}, upsert = True)
			except TypeError as e:
				pass


	def freq(self, item):
		for word in item['words']:
			word_id = w.find_one({'word': word}, fields = ['_id'])['_id']
			f.update({'_id': word_id}, {"$inc": {'freq': 1}})
