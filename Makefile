FLAGS =
clear:
	make reset && make init && make on
reset:
	python -c\
		'import sys, os;\
		sys.path.extend(["../", "spyder/"]);\
		from pymongo import MongoClient;\
		from defines import *;\
		r = MongoClient(os.environ.get("MONGOHQ_URL"));\
		r.drop_database(DB_NAME);'
	rm -f spyder/*.pyc
	rm -f spyder/spiders/*.pyc
	rm -f scripts/*.pyc
	rm -f data/*

crawl:
	rm -f *.pyc
	scrapy crawl google $(FLAGS)

init:
	python -c\
		'import sys, os;\
		sys.path.extend(["../", "spyder/"]);\
		from pymongo import MongoClient;\
		from defines import *;\
		r = MongoClient(os.environ.get("MONGOHQ_URL"));\
		db = r[DB_NAME];\
		c = db[CRAWLER_DATA];\
		c.insert({"spider": "google", "processed_ctr": 0});'


on:
	python -c\
		'import sys, os;\
		sys.path.extend(["../", "spyder/"]);\
		from pymongo import MongoClient;\
		from defines import *;\
		r = MongoClient(os.environ.get("MONGOHQ_URL"));\
		db = r[DB_NAME];\
		c = db[CRAWLER_DATA];\
		c.update({"spider": "google"}, {"$$set": {"POWER_SWITCH": "ON"}});'

off:
	python -c\
		'import sys, os;\
		sys.path.extend(["../", "spyder/"]);\
		from pymongo import MongoClient;\
		from defines import *;\
		r = MongoClient(os.environ.get("MONGOHQ_URL"));\
		db = r[DB_NAME];\
		c = db[CRAWLER_DATA];\
		c.update({"spider": "google"}, {"$$set": {"POWER_SWITCH": "OFF"}});'

process:
	python scripts/remap.py
	python scripts/indexbuilder.py

rank:
	python scripts/rankmap.py
