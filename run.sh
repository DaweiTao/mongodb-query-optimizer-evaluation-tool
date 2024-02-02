#!/bin/sh

# Build the config file matching the version being tested
# v=orig
# v=with-coll
# v=with-coll-with-fix
v=${1:orig}
rm -f config.ini && sed -e 's/^[^;].*result-/;\0/' -e 's/^;\(.*result-'$v'\/\)/\1/' < experiment/config.ini > config.ini

rm -rf ../assets ../results
mkdir ../assets ../results

# Stop / start MongoDB?
pkill -9 mongod
sleep 1
rm -rf data ; mkdir data
./build/install-$v/bin/mongod --dbpath=`pwd`/data --logpath=`pwd`/mongod.log --fork
sleep 1

# Run the experiments
c=uniform
n=5
./venv/bin/python experiment/experiment_core.py $c -b $c
./venv/bin/python experiment/experiment_core.py $c -q $n

# Remove indexes if necessary
unset rm1 rm2
indexes=${2:-cover}
case $indexes in
both|single)
	rm1='db.uniform.dropIndex("coverIdx")' ;;
esac
case $indexes in
single)
	rm2='db.uniform.dropIndex("aIdx")' ;;
esac

./build/install-orig/bin/mongo <<EOF
use experiment0
$rm1
$rm2
EOF

./venv/bin/python experiment/experiment_core.py $c -r
