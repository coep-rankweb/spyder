FLAGS =
clear:
	make reset && make init && make on
reset:
	python -c 'from control import *; reset();'
	rm -f spyder/*.pyc
	rm -f spyder/spiders/*.pyc
	rm -f scripts/*.pyc
	rm -f data/*

crawl:
	rm -f *.pyc
	scrapy crawl google $(FLAGS)

init:
	python -c 'import control; control.init();'


on:
	python -c 'import control; control.on();'

off:
	python -c 'import control; control.off();'

process:
	python scripts/remap.py
	python scripts/indexbuilder.py

rank:
	python scripts/rankmap.py
