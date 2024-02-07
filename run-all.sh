#!/bin/bash

expdir=$(dirname $0)
cd $expdir

if ! [ -f ../mongodb-src-r7.0.1/build/install-orig/bin/mongod ] ; then
	echo 2>&1 "MongoDB binaries expected in mongodb-src-r7.0.1"
	exit 1
fi
ln -s ../mongodb-src-r7.0.1/build .

# Install requirements for the experiment code
virtualenv venv
venv/bin/pip install -r requirements.txt

# Run all of the experiments
for v in orig with-coll with-coll-with-fix ; do
	for i in cover both single ; do
		./run.sh $v $i
	done
done
