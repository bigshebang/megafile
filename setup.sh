#!/usr/bin/env bash
#only tested on ubuntu 16.04 base image/install
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
