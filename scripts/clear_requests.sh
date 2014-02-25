#!/bin/bash

wc -l /home/nvidia/kernel_panic/core/spyder/data/* | python /home/nvidia/kernel_panic/core/spyder/scripts/line_counter.py
if [ $? -ge 0 ]
then
	#echo "HELLO!"
	redis-cli SHUTDOWN
	echo elonmusk | sudo -S -k poweroff
fi
