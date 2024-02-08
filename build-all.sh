#!/bin/bash
runstamp=$1
# Build MongoDB binaries and setup to run FPTP experiments
echo "Started    :: Build MongoDB Binaries and setup to run FPTP experiments" >> build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> build-all.${runstamp}.txt
echo "Started :: Download mongodb-7.0.1 source" >> build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> build-all.${runstamp}.txt
wget -c https://fastdl.mongodb.org/src/mongodb-src-r7.0.1.tar.gz
tar xvf mongodb-src-r7.0.1.tar.gz
cd mongodb-src-r7.0.1
echo "Finished:: Build MongoDB Binaries and setup to run FPTP experiments" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt

## Install Python requirements for the MongoDB build
echo "Started: :Install Python requirements for the MongoDB build" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt
virtualenv venv
./venv/bin/pip install -r buildscripts/requirements.txt 
echo "Finished::  Install Python requirements for the MongoDB build" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt

echo "Started :: MongoDB 7.0.1 Original version patch build" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt
patch -p1 < ../mongodb-fptp-paper-main/mongoversions/7.0.1-V0-build.diff
venv/bin/python buildscripts/scons.py --disable-warnings-as-errors --ninja -Q MONGO_VERSION=7.0.1-orig build.ninja
ninja-build install-mongo
ninja-build install-mongod
mv build/install build/install-orig
echo "Finished :: MongoDB 7.0.1 Original version patch build" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt

echo "Started :: MongoDB 7.0.1 Original version patch build" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt
patch -p1 < ../mongodb-fptp-paper-main/mongoversions/7.0.1-V1-with-coll.diff
venv/bin/python buildscripts/scons.py --disable-warnings-as-errors --ninja -Q MONGO_VERSION=7.0.1-with-coll build.ninja
ninja-build install-mongod
mv build/install build/install-with-coll
echo "Finished:: MongoDB 7.0.1 Original version patch build" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt

echo "Started :: MongoDB 7.0.1 Original version patch build" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt
patch -p1 < ../mongodb-fptp-paper-main/mongoversions/7.0.1-V2-with-fix.diff
venv/bin/python buildscripts/scons.py --disable-warnings-as-errors --ninja -Q MONGO_VERSION=7.0.1-with-coll-with-fix build.ninja
mv build/install build/install-with-coll-with-fix
echo "Finished:: MongoDB 7.0.1 Original version patch build" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt

echo "Finished:: Build MongoDB Binaries and setup to run FPTP experiments" >> ../build-all.${runstamp}.txt
echo "Timedstamp :: ", `date +%s` >> ../build-all.${runstamp}.txt
