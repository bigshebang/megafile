#!/usr/bin/env bash
# only tested on ubuntu 16.04 base image/install
DB_USER=root
DB_PASSWORD=password


packages=""
for line in requirements.txt; do
	packages="$packages $line"
done

sudo apt install $packages -y

mysql -u "$DB_USER" -p"$DB_USER" < create_db.sql
mysql -u "$DB_USER" -p"$DB_USER" < create_user.sql