#!/bin/sh

# Get the full directory of the experiment code
expdir=`dirname $0`
expdir=$(cd $expdir && pwd)

# Command line argument processing
# v=orig
# v=with-coll
# v=with-coll-with-fix
v=${1:-orig}
indexes=${2:-cover}

mdbver=7.0.1

export PYTHONPATH=$PYTHONPATH:$expdir

# Setup the results directory and change to there
d=../results-$indexes/v$mdbver
[ $v != 'orig' ] && d=$d-$v

echo "Creating results directory $d"
rm -rf $d
mkdir -p $d
cd $d

# Redirect output to a file in the results directory
exec > run.sh.out 2>&1

echo "FPTP for MongoDB $mdbver run.sh $*"
date

# Generate the config.ini file used by scripts below
sed -e 's/^[^;].*result-/;\0/' -e 's/^;\(.*result-'$v'\/\)/\1/' < $expdir/experiment/config.ini > config.ini

# Stop / start MongoDB
pkill -9 mongod
sleep 1
rm -rf data ; mkdir data
$expdir/build/install-$v/bin/mongod --dbpath=`pwd`/data --logpath=`pwd`/mongod.log --fork
sleep 1

# Setup the experiments
c=uniform
n=5
$expdir/venv/bin/python $expdir/experiment/experiment_core.py $c -b $c
$expdir/venv/bin/python $expdir/experiment/experiment_core.py $c -q $n

# Remove indexes if necessary
unset rm1 rm2
case $indexes in
both|single)
	rm1='db.uniform.dropIndex("coverIdx")' ;;
esac
case $indexes in
single)
	rm2='db.uniform.dropIndex("aIdx")' ;;
esac

$expdir/build/install-orig/bin/mongo <<EOF
use experiment0
$rm1
$rm2
EOF

# Run the experiments
$expdir/venv/bin/python $expdir/experiment/experiment_core.py $c -r

# Process the results, generate graphs
$expdir/venv/bin/python $expdir/processing/analyze_result.py $c $indexes
