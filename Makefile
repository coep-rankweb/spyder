crawl:
	rm -f data/*
	rm -f *.[mt]x[t] *.pyc
	scrapy crawl google
on:
	python -c "import sys; sys.path.append('../'); from datastore import Datastore; r = Datastore(); r.set('POWER_SWITCH', 'ON')"
off:
	python -c "import sys; sys.path.append('../'); from datastore import Datastore; r = Datastore(); r.set('POWER_SWITCH', 'OFF')"
