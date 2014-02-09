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
		sys.path.extend("../");\
		from datastore import Datastore;\
		from defines import *;\
		Datastore.factory().set(CRAWLER_DATA, {"spider": "google"});'


on:
	python -c\
		'import sys;\
		sys.path.extend("../");\
		from datastore import Datastore;\
		from defines import *;\
		Datastore.factory().update(POWER_SWITCH, "ON");'

off:
	python -c\
		'import sys;\
		sys.path.extend("../");\
		from datastore import Datastore;\
		from defines import *;\
		Datastore.factory().update(POWER_SWITCH, "OFF");'

process:
	python scripts/remap.py
	python scripts/indexbuilder.py

rank:
	python scripts/rankmap.py
