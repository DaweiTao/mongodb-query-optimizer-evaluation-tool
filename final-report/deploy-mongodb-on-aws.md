Deploy MongoDB On AWS Instances
====
For this project, it is recommended to deploy different versions of MongoDB on different AWS instances.
This document provide all the details of how to compile MongoDB source code and deploy the build
on the AWS instance. 

Where to Get Source Code
----
We use three different versions of MongoDB for the experiment, including v4.4.0 release and two other modifed versions:

* V0: the original MongoDB v4.4.0 release
    * `$ wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon2-4.4.0.tgz`
* V1: we add collection scan to query plan candidates (based on MongoDB v4.4.0 source code)
    * [V1 release](https://github.com/DaweiTao/mongo/releases/tag/v4.4.0-collscan-added)
* V2: we adjust the productvity of all fetch operations (based on MongoDB v4.4.0 source code)
    * [V2 release](https://github.com/DaweiTao/mongo/releases/tag/v4.4.0-fptp-mod)

The query optimizer of MongoDB V0 never chooses collection scan. Because collection
 scan is not in the query plan candidates. In V1 we add collection scan to query plan candidates. The query optimizer 
considers collection scan as a query plan candidate, but it never chooses collection scan. We find that
the query optimizer has a preference bias towards fetch operations.
Therefore, in V2 we penalize the productivity score of all fetch operations. As a result, the preference
bias problem is fixed. 

AWS Instance Minimum Requirement
----
| Instance Size | vCPU | Memory (GiB) | Instance Storage(GiB) |
|---------------|------|:------------:|-----------------------|
| t2.xlarge     | 4    | 16           | 50                    |

**Note**: SSD is recommended. 

Building MongoDB From Source 
----
To build MongoDB, you will need:
* A modern C++ compiler capable of compiling C++17. One of the following is required:
    * GCC 8.2 or newer
    * Clang 7.0 (or Apple XCode 10.2 Clang) or newer
    * Visual Studio 2019 version 16.4 or newer (See Windows section below for details)
* On Linux and macOS, the libcurl library and header is required. MacOS includes libcurl.
    * Fedora/RHEL - `dnf install libcurl-devel`
    * Ubuntu/Debian - `libcurl-dev` is provided by three packages. Install one of them:
      * `libcurl4-openssl-dev`
      * `libcurl4-nss-dev`
      * `libcurl4-gnutls-dev`
* Python 3.7.x and Pip modules:
  * See the section "Python Prerequisites" below.
* About 13 GB of free disk space for the core binaries (`mongod`,`mongos`, and `mongo`) and about 600 GB for the install-all target.

Scons Prerequisites
----
To install lzma dlevel （Devel libraries & headers for liblzma) on Linux, run:

    $ yum install -y xz-devel

Install mongod
----
Upgrade g++ version:
* Check [this guide](https://medium.com/@bipul.k.kuri/install-latest-gcc-on-centos-linux-release-7-6-a704a11d943d)
for more information
* If the mirror in the article doesn't work, try this one:\
https://ftp.gnu.org/gnu/gcc/gcc-8.2.0/gcc-8.2.0.tar.gz
* All steps together (shell script):
```shell script
#!/bin/sh
GCC_VERSION=8.2.0
sudo yum -y update
sudo yum -y install bzip2 wget gcc gcc-c++ gmp-devel mpfr-devel libmpc-devel make
gcc --version
wget http://gnu.mirror.constant.com/gcc/gcc-$GCC_VERSION/gcc-$GCC_VERSION.tar.gz
tar zxf gcc-$GCC_VERSION.tar.gz
mkdir gcc-build
cd gcc-build
../gcc-$GCC_VERSION/configure --enable-languages=c,c++ --disable-multilib
make -j$(nproc)
sudo make install
gcc --version
cd ..
rm -rf gcc-build
```

Install install libcurl, run:

```
$ yum install -y curl-devel
$ yum install -y openssl-devel
```

Install lzma dlevel (Devel libraries & headers for liblzma), run:

    $ yum install -y xz-devel

Build from source code, run:

    $ python3 buildscripts/scons.py -j4 --disable-warnings-as-errors install-core

**Note**: We need **mongod** and **mongo**. The following targets can be named on the scons command line to build
only certain components:

* `install-mongod` 
* `install-mongos`
* `install-mongo` or `install-shell`
* `install-servers` (includes `mongod` and `mongos`)
* `install-core` (includes `mongod`, `mongos`, `mongo`)
* `install-all`

Where to find Binaries
----
`$DESTDIR/$PREFIX`. `DESTDIR` by default is `build/install` while
`PREFIX` is by default empty. This means that with all of the listed
targets all built binaries will be in `build/install/bin` by default.

Run Mongo Daemon
----
Create database

    $ mkdir -p /data/db

Modify the config file of MongoDB

    $ vim /etc/mongod.conf
    
Here is an example of config file

```
net:
    port: 27017
    bindIp: 0.0.0.0   #default value is 127.0.0.1
storage:
    dbPath: /data/db
```
    
create MongoDB Admin user

```shell script
$ mongo
> use admin
> db.createUser({user: "admin", pwd: "admin", roles:[ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]})
```
**Note**: you should use your own username and password (specified in `user` and `pwd`)

Run mongod

    $ mongod -f /etc/mongod.conf &

Connection String
----
For this project, a valid MongoDB connection string should be provided in order to run all the experiment.
An example of a valid MongoDB connection string:

```python
connection_str = 'mongodb://<username>:<password>@ec2-123-123-123-123.ap-southeast-2.compute.amazonaws.com:27017/'
```

**Note** Replace <username> and <password> with your own username and password

More on this topic: [official guide](https://docs.mongodb.com/manual/reference/connection-string/)