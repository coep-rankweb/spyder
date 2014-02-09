from scrapy import log
import os
import sys
sys.path.append(os.path.abspath('../'))
from defines import *
from datastore import Datastore
from scrapy.exceptions import DropItem
import nltk
from unidecode import unidecode
from throttler import throttle, final_throttle
import itertools


class DuplicatesFilter(object):
	'''
	Filters duplicate urls
	Assigns each url a unique id
	Sets url -> id and id -> url in redis
	Indexes inlinks and outlinks
	'''
	def __init__(self):
		self.r = Datastore()
		self.URL_CTR = itertools.count()

	@throttle
	def process_item(self, item, spider):
		if self.r.find_one(URL_DATA, {'url': item['url']}): #duplicate
			raise DropItem
		else: #process new item
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
		self.r.insert(URL_DATA, {'id': url_id, 'url': item['url']})

		for link in item['link_set']:
			res = self.r.find_one(URL_DATA, {'url': link})
			if not res:
				new_url_id = self.URL_CTR.next()
				self.r.insert(URL_DATA, {'id': new_url_id, 'url': link})
			else:
				new_url_id = res['id']
			self.r.update(URL_DATA, {'id': url_id}, {"$addToSet": {"out_links": new_url_id}})

class TextExtractor(object):
	''' Extracts text from the raw_html field of the item '''
	@throttle
	def process_item(self, item, spider):
		if not item['raw_html']:
			item['extracted_text'] = ""
		else:
			temp = nltk.clean_html(item['raw_html'])
			try: temp = unicode(temp, encoding = "UTF-8")
			except: pass
			item['extracted_text'] = unidecode(temp)
		return item


class KeywordExtractor(object):
	'''
	Extracts keywords from title, extracted_text, meta_description
	'''
	def __init__(self):
		self.r = Datastore()
		self.WORD_CTR = itertools.count()
		self.stemmer = nltk.stem.PorterStemmer()
		self.stopwords = set(nltk.corpus.stopwords.words('english'))

	@throttle
	def process_item(self, item, spider):
		text = item['title'] + " . " + item['extracted_text'] + " . " + item['meta_description']
		words = nltk.wordpunct_tokenize(text)
		cleaned_words = set(words) - self.stopwords
		cleaned_words = [self.clean(w) for w in cleaned_words if w.isalnum() and len(w) > 1 and not w.isdigit()]
		item['words'] = cleaned_words
		self.buildWordIndex(item)

		return item

	def buildWordIndex(self, item):
		'''
		Get current url id
		For each word in current url's text,
			add the url to the set of urls which contain that word
		'''
		url_id = self.r.find_one(URL_DATA, {"url": item['url']}, fields = ['id'])['id']
		word_id = -1
		for word in item['words']:
			res = self.r.find_one(WORD_DATA, {'word': word}, fields = ['id'])
			if res:
				word_id = res['id']
			else:
				word_id = self.WORD_CTR.next()
				self.r.insert(WORD_DATA, {'word': word, 'id': word_id})
			self.r.update(WORD_DATA, {'id': word_id}, {"$addToSet": {"present_in": url_id}})
			self.r.update(URL_DATA, {'id': url_id}, {"$addToSet": {"word_vec": word_id}})

	def clean(self, s):
		return self.stemmer.stem(s.lower())

class Analytics(object):
	'''
	Text analytics (if any)
	'''
	def __init__(self):
		self.r = Datastore()
		self.TOP_N = 5
		self.bgm = nltk.collocations.BigramAssocMeasures
		self.SCORER_FN = self.bgm.likelihood_ratio
	@final_throttle
	def process_item(self, item, spider):
		self.digram(item)
		self.freq(item)
		return item

	def digram(self, item):
		finder = nltk.collocations.BigramCollocationFinder.from_words(item['words'])
		digrams = finder.nbest(self.SCORER_FN, self.TOP_N)
		for digram in digrams:
			base_id = self.r.find_one(WORD_DATA, {'word': digram[0]}, fields = ['id'])['id']
			next_id = self.r.find_one(WORD_DATA, {'word': digram[1]}, fields = ['id'])['id']
			self.r.update(COLLOCATIONS_DATA, {'base': base_id}, {"$inc": {'next.' + str(next_id): 1}})

	def freq(self, item):
		for w in item['words']:
			word_id = self.r.find_one(WORD_DATA, {'word': w}, fields = ['id'])['id']
			self.r.update(FREQ_DATA, {'id': word_id}, {"$inc": {'freq': 1}})
