#!/bin/bash

# Install requirements for the experiment code
cd mongodb-fptp-paper-main
virtualenv venv
venv/bin/pip install requirements.txt
ln -s ../mongodb-src-r7.0.1/build .
cd ..

# Build MongoDB binaries and setup to run FPTP experiments
wget -c https://fastdl.mongodb.org/src/mongodb-src-r7.0.1.tar.gz
tar xvf mongodb-src-r7.0.1.tar.gz
cd mongodb-src-r7.0.1

## Install Python requirements for the MongoDB build
virtualenv venv
./venv/bin/pip install -r buildscripts/requirements.txt 

patch -p1 < ../mongodb-fptp-paper-main/mongoversions/7.0.1-V0-build.diff
venv/bin/python buildscripts/scons.py --disable-warnings-as-errors --ninja -Q MONGO_VERSION=7.0.1-orig build.ninja
ninja-build install-mongo
ninja-build install-mongod
mv build/install build/install-orig

patch -p1 < ../mongodb-fptp-paper-main/mongoversions/7.0.1-V1-with-coll.diff
venv/bin/python buildscripts/scons.py --disable-warnings-as-errors --ninja -Q MONGO_VERSION=7.0.1-with-coll build.ninja
ninja-build install-mongod
mv build/install build/install-with-coll

patch -p1 < ../mongodb-fptp-paper-main/mongoversions/7.0.1-V2-with-fix.diff
venv/bin/python buildscripts/scons.py --disable-warnings-as-errors --ninja -Q MONGO_VERSION=7.0.1-with-coll-with-fix build.ninja
mv build/install build/install-with-coll-with-fix
