FLAGS =
clear:
	make reset && make init && make on
reset:
	redis-cli flushdb
	python -c 'from control import *; reset();'
	rm -rf spyder/*.pyc
	rm -rf spyder/spiders/*.pyc
	rm -rf scripts/*.pyc
	rm -rf data/*

crawl:
	rm -f *.pyc
	scrapy crawl google $(FLAGS) 2> data/timelog

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
