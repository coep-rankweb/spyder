FLAGS =

reset:
	python reset.py

crawl:
	rm -f data/*
	rm -f *.[mt]x[t] *.pyc
	scrapy crawl google $(FLAGS) 2> data/timelog

on:
	python -c "import sys; sys.path.append('../'); from datastore import Datastore; r = Datastore(); r.set('POWER_SWITCH', 'ON')"

off:
	python -c "import sys; sys.path.append('../'); from datastore import Datastore; r = Datastore(); r.set('POWER_SWITCH', 'OFF')"

process:
	python remap.py
	python indexbuilder.py

rank:
	python rankmap.py
