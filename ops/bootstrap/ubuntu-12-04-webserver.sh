#!/bin/bash

wget -O /etc/apt/sources.list.d/newrelic.list http://download.newrelic.com/debian/newrelic.list

apt-key adv --keyserver hkp://subkeys.pgp.net --recv-keys 548C16BF

apt-get update

apt-get install -y newrelic-sysmond

nrsysmond-config --set license_key=$NEW_RELIC_LICENSE_KEY

/etc/init.d/newrelic-sysmond start

apt-get install -y git

apt-get install -y python-setuptools
apt-get install -y python-psycopg2
apt-get install -y libpq-dev python-dev
easy_install pip

pip install virtualenv

virtualenv --no-site-packages ureport_env

sh ~/ureport_env/bin/activate

mkdir code

cd code

git clone "https://github.com/unicefuganda/ureport.git" 

cd ureport

git submodule update --init

pip install -r pip-requires.txt

cd ureport_project
./manage.py syncdb
