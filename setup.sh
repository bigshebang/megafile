#!/usr/bin/env bash
#only tested on ubuntu 16.04 base image/install
DB_USER=root
DB_PASSWORD=password


#install necessary packages for apache and php7 setup
packages=""
for line in requirements.txt; do
	packages="$packages $line"
done

sudo apt install $packages -y


#set up DB stuff
mysql -u "$DB_USER" -p"$DB_USER" < create_db.sql
mysql -u "$DB_USER" -p"$DB_USER" < create_user.sql


#set up perl CGI stuff
sudo a2enmod perl cgi
sudo sed -i 's|/usr/lib/cgi-bin|/var/www/megafile/cgi-bin|' /etc/apache2/conf-enabled/serve-cgi-bin.conf
