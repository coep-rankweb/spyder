#! /bin/bash

SCRIPT_PATH="/home/nvidia/kernel_panic/core/spyder/scripts"
DATA_PATH="/home/nvidia/kernel_panic/core/spyder/data"


num_nodes=`redis-cli scard PROCESSED_SET | cut -f 2`
num_edges=`wc -l $DATA_PATH/web.mtx | cut -f 1 -d " "`
num_edges=`expr $num_edges - 3`

function dump() {
	redis-cli SHUTDOWN
	echo elonmusk | sudo -S -k cp /var/redis/redis_6379/dump.rdb /home/nvidia/kernel_panic/core/snapshot/`date +dump_%d%b@%H_%M`_$1
	echo elonmusk | sudo -S -k service redis start
	sleep 600
}



# Builds HASH2ID and web.mtx(without third line)
python $SCRIPT_PATH/indexer.py



# Adds third line to web.mtx
head -2 $DATA_PATH/web.mtx > $DATA_PATH/new_web.mtx
printf "%d\t%d\t%d\n" $num_nodes $num_nodes $num_edges >> $DATA_PATH/new_web.mtx
tail -n +4  $DATA_PATH/web.mtx >> $DATA_PATH/new_web.mtx
mv $DATA_PATH/new_web.mtx $DATA_PATH/web.mtx



# Take the dump
cp $DATA_PATH/*.txt $DATA_PATH/web.mtx $DATA_PATH/matrix.mtx /home/nvidia/kernel_panic/core/snapshots/
dump before_rankmap



# Build in_links and out_links hashes
# 544 = 8 * 4 + 512 (512 - url length)
dd bs=544 count=$num_nodes if=/dev/zero of=$DATA_PATH/meta
gcc linkstore.c -lhiredis -o linkstore
./linkstore



# Calculate the rank
make -C /home/nvidia/kernel_panic/core/cusp new_gpu
python $SCRIPT_PATH/rankmap.py



# Take the dump
dump after_rankmap



# doc-vector
python $SCRIPT_PATH/doc_index.py



# If everything works (or not)
echo "elonmusk" | sudo -S -k poweroff
