#!/bin/bash

function dump() {
	redis-cli SHUTDOWN
	echo elonmusk | sudo -S -k cp /var/redis/redis_6379/dump.rdb /home/nvidia/kernel_panic/core/snapshot/`date +dump_%H_%M`_$1
	echo elonmusk | sudo -S -k service redis start
}

wc -l /home/nvidia/kernel_panic/core/spyder/data/* | python /home/nvidia/kernel_panic/core/spyder/scripts/line_counter.py
if [ $? -ge 0 ]
then
	dump raw_crawl

	python /home/nvidia/kernel_panic/core/spyder/scripts/hash_scripts/indexer.py
	dump indexed

	python /home/nvidia/kernel_panic/core/spyder/scripts/hash_scripts/doc_index.py
	dump doc_vector

	make -C /home/nvidia/kernel_panic/core/cusp/ gpu
	python /home/nvidia/kernel_panic/core/spyder/scripts/hash_scripts/rankmap.py
	dump ranked

	echo elonmusk | sudo -S -k poweroff
fi
