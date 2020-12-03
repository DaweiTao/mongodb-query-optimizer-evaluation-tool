Building MongoDB From Source 
================
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


Source Code
------
* V0: MongoDB v4.4.0 release
    * `$ wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon2-4.4.0.tgz`
* V1: add collection scan to query plan candidates (based on MongoDB v4.4.0 source code)
    * https://github.com/DaweiTao/mongo/archive/mongo-with-collscan.tar.gz
* V2: adjust the productvity of all fetch operations (based on MongoDB v4.4.0 source code)
    * https://github.com/DaweiTao/mongo/archive/mongo-wiith-collscan-with-fix.tar.gz


Python Prerequisites
------

In order to build MongoDB, Python 3.7+ is required, and several Python
modules must be installed. Note that on macOS the system python is
still python2. You will need to use homebrew or macports or similar to
obtain python3.

To install the required Python modules, run:

    $ python3 -m pip install -r etc/pip/compile-requirements.txt

Installing the requirements inside a python3 based virtualenv
dedicated to building MongoDB is recommended.

Note: In order to compile C-based Python modules, you'll also need the
Python and OpenSSL C headers. Run:

* Fedora/RHEL - `dnf install python3-devel openssl-devel`
* Ubuntu/Debian - `apt-get install python3.7-dev libssl-dev`


Scons Prerequisites
------
To install lzma dlevel （Devel libraries & headers for liblzma) on Linux, run:

    $ yum install -y xz-devel
    

Build Source Code on a AWS Linux 2 instance
------
Upgrade g++ version:
* https://medium.com/@bipul.k.kuri/install-latest-gcc-on-centos-linux-release-7-6-a704a11d943d
* https://ftp.gnu.org/gnu/gcc/gcc-8.2.0/gcc-8.2.0.tar.gz

Install install libcurl, run:
```
$ yum install -y curl-devel
$ yum install -y openssl-devel
```
Install lzma dlevel (Devel libraries & headers for liblzma), run:

    $ yum install -y xz-devel
    
Build from source code, run:

    $ python3 buildscripts/scons.py -j4 --disable-warnings-as-errors install-mongod

**Note**: The following targets can be named on the scons command line to build
only certain components:

* `install-mongod`
* `install-mongos`
* `install-mongo` or `install-shell`
* `install-servers` (includes `mongod` and `mongos`)
* `install-core` (includes `mongod`, `mongos`, `mongo`)
* `install-all`

Where to find Binaries
------
`$DESTDIR/$PREFIX`. `DESTDIR` by default is `build/install` while
`PREFIX` is by default empty. This means that with all of the listed
targets all built binaries will be in `build/install/bin` by default.

