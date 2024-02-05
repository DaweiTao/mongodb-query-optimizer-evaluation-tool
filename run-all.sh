#!/bin/bash

expdir=$(dirname $0)

# Run all of the experiments
for v in orig with-coll with-coll-with-fix ; do
	for i in cover both single ; do
		$expdir/run.sh $v $i
	done
done
