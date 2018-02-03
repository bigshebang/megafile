#!/usr/bin/env bash
#only tested on ubuntu 16.04 base image/install

#Instructions notes i guess
#run this on the app server and it should install all the necessary packages
#the packages for data storage (mysql and redis) are not included here because
#	they are meant to be installed on a separate server which is just a data
#	store server. also there's no ubuntu package for redis
#i should probably note that requirements.txt in the root isn't the typical
#	pip packages for a python project, it's apt packages instead because i'm
#	dirty. but flask/requirements.txt does have pip packages in it

DB_USER=root
DB_PASSWORD=password


#install necessary packages for apache and php7 setup
packages=""
lines=$(cat requirements.txt)
for line in $lines; do
	packages="$packages $line"
done

sudo apt install $packages -y


#set up DB stuff
mysql -u "$DB_USER" -p"$DB_USER" < create_db.sql
mysql -u "$DB_USER" -p"$DB_USER" < create_user.sql


#enable mod_headers
sudo a2enmod  headers
