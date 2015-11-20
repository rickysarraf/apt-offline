### apt-offline

apt-offline is an offline package management tool written in the
Python Programming Language. This program, as of now, is intended for
people using Debian (And Debian based) systems.

It can help you install/upgrade packages, and their dependencies, on a
Debian box with no direct internet connection. It can also download
full bug report (Debian only) for those packages.

For Developers, it can help you download a source deb package, along
with all its build dependencies.

This program allows leveraging the power of Debian (more precisely
APT) onto a completely disconnected machine. Most of the people with
slow or no internet connection (most of those in India/Nepal/Pakistan
and nearby countries), have not considered using Debian (or Debian
derived distributions), because Debian's real taste is experienced
when it is connected to the internet.

This utility is an attempt in making that problem eradicate. I hope
this utility comes of use to you. I'd be eager to hear your
comments/suggestions. Feel free to drop an email at rrs _AT_
researchut |DOT| com

### Dedication
This software is dedicated to the memory of my father Santosh Kumar
Sarraf. We miss you a lot.



### CI Testcase Status
[![Build Status](https://travis-ci.org/rickysarraf/apt-offline.svg?branch=master)]
(https://travis-ci.org/rickysarraf/apt-offline)

### py3-port testing requirements.

Since in the py3-port branch we use python-apt for some work related
to packages, tests will not run on CI systems unless python-apt is
present in the virtualenv which runs test.

Sadly the installation of python-apt from pypi is not possible as its
outdated. One more way to do is get python-apt from Git but this also
breaks as python-apt depends on cx11 features (latest branch).

So as of now CI status will be borked till we find a way to get it
working.

#### Testing Requirements
1. python-apt
2. libapt-pkg-dev
3. python-dev
4. python3-dev

If these are not installed testing will not work properly. Even for
using tox this is needed.

### Python3 and Refactoring Port CI and Coverage Status
[![Build Status](https://travis-ci.org/copyninja/apt-offline.svg?branch=py3-port)](https://travis-ci.org/copyninja/apt-offline)
[![Coverage Status](https://coveralls.io/repos/copyninja/apt-offline/badge.svg?branch=py3-port&service=github)](https://coveralls.io/github/copyninja/apt-offline?branch=py3-port)
