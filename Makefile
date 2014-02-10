FLAGS = --nolog

reset:
	python scripts/reset.py

crawl:
	rm -f data/*
	rm -f *.[mt]x[t] *.pyc
	scrapy crawl google $(FLAGS) 2> data/timelog

on:
	python -c "import sys; sys.path.append('../'); from datastore import Datastore; r = Datastore(); r.set('POWER_SWITCH', 'ON')"

off:
	python -c "import sys; sys.path.append('../'); from datastore import Datastore; r = Datastore(); r.set('POWER_SWITCH', 'OFF')"

process:
	python scripts/remap.py
	python scripts/indexbuilder.py

rank:
	python scripts/rankmap.py
