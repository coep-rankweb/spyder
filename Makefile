FLAGS = -s JOBDIR=data/google_spider
#FLAGS =

reset:
	python scripts/reset.py

crawl:
	rm -rf data/*
	rm -f *.[mt]x[t] spyder/*.pyc
	scrapy crawl google $(FLAGS) 2>> data/timelog

on:
	python -c "import sys; sys.path.append('../'); from datastore import Datastore; r = Datastore(); r.set('POWER_SWITCH', 'ON')"

off:
	python -c "import sys; sys.path.append('../'); from datastore import Datastore; r = Datastore(); r.set('POWER_SWITCH', 'OFF')"

process:
	python scripts/remap1.py
#	python scripts/indexbuilder.py

rank:
	python scripts/rankmap.py
