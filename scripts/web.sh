#! /bin/bash


# so that it will fail on the first error
set -e

SCRIPT_PATH="/home/nvidia/kernel_panic/core/spyder/scripts"
DATA_PATH="/home/nvidia/kernel_panic/core/spyder/data"
SNAPSHOT_PATH="/home/nvidia/kernel_panic/core/snapshot"


function dump() {
		redis-cli SHUTDOWN
		echo elonmusk | sudo -S -k cp /var/redis/redis_6379/dump.rdb $SNAPSHOT_PATH/`date +dump_%d%b@%H_%M`_$1
		echo elonmusk | sudo -S -k service redis start
		sleep 600
}


#dump before_rankmap


python $SCRIPT_PATH/remote_dumper.py before_indexer

# Builds HASH2ID, ID2HASH and web.mtx(without third line)
python $SCRIPT_PATH/indexer.py

python $SCRIPT_PATH/emailer.py "Completed indexing"

python $SCRIPT_PATH/remote_dumper.py after_indexer



# web.mtx has been created. Analyze it to get its three parameters for the third line in web.mtx
num_nodes=`python -c "import redis; r = redis.Redis('10.1.99.15'); print r.scard('PROCESSED_SET');"`
num_edges=`wc -l $DATA_PATH/web.mtx | cut -f 1 -d " "`
num_edges=`expr $num_edges - 3`

# Adds third line to web.mtx
head -2 $DATA_PATH/web.mtx > $DATA_PATH/new_web.mtx
printf "%d\t%d\t%d\n" $num_nodes $num_nodes $num_edges >> $DATA_PATH/new_web.mtx
tail -n +4  $DATA_PATH/web.mtx >> $DATA_PATH/new_web.mtx
mv $DATA_PATH/new_web.mtx $DATA_PATH/web.mtx



# Take the dump
cp $DATA_PATH/*.txt $DATA_PATH/web.mtx $DATA_PATH/in_matrix.mtx $SNAPSHOT_PATH 


python $SCRIPT_PATH/emailer.py "Added third line to web.mtx and stored the dump"


# generate inlinks, outlinks on remote redis
python $SCRIPT_PATH/linkstore.py



python $SCRIPT_PATH/emailer.py "generated inlinks and outlinks"


# Calculate the rank
make -C /home/nvidia/kernel_panic/core/cusp new_gpu
python $SCRIPT_PATH/rankmap.py



python $SCRIPT_PATH/emailer.py "ranked the graph"


# Take the dump
dump after_rankmap



# doc-vector
python $SCRIPT_PATH/doc_index.py


python $SCRIPT_PATH/emailer.py "generated url word vectors. SHUTTING DOWN."


# If everything works (or not)
echo "elonmusk" | sudo -S -k poweroff
