FLAGS =

reset:
	python -c\
		'from datastore import Datastore;\
		Datastore().flushdb();'

crawl:
	rm -f *.pyc
	scrapy crawl google $(FLAGS)

init:
	python -c\
		'import sys;\
		sys.path.extend(["../", "spyder/"]);\
		from datastore import Datastore;\
		from defines import *;\
		Datastore().insert(CRAWLER_DATA, {"spider": "google"});'


on:
	python -c\
		'import sys;\
		sys.path.extend(["../", "spyder/"]);\
		from datastore import Datastore;\
		from defines import *;\
		Datastore().update(CRAWLER_DATA, {"spider": "google"}, {"$$set": {"POWER_SWITCH": "ON"}});'

off:
	python -c\
		'import sys;\
		sys.path.extend(["../", "spyder/"]);\
		from datastore import Datastore;\
		from defines import *;\
		Datastore().update(CRAWLER_DATA, {"spider": "google"}, {"$$set": {"POWER_SWITCH": "OFF"}});'

process:
	python scripts/remap.py
	python scripts/indexbuilder.py

rank:
	python scripts/rankmap.py
