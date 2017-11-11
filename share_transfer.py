#!/usr/bin/env python
import redis
import ConfigParser
from sqlalchemy import create_engine, select, func, MetaData
from sqlalchemy.exc import IntegrityError
from time import sleep
import re

#regex to validate a share message
valid_share = re.compile("^(?P<from>\d+)\s+(?P<to>\d+)$")

def get_conf(conf_file="config.ini"):
	config = ConfigParser.ConfigParser()
	config.read(conf_file)
	conf_dict = {}

	for section in config.sections():
		conf_dict[section] = {}
		for item in config.items(section):
			conf_dict[section][item[0]] = item[1].strip('"')

	return conf_dict

def create_redis_conn(redis_conf):
	return redis.Redis(
	    host=redis_conf['host'],
	    port=redis_conf['port'], 
	    password=redis_conf['password']
    )

def create_db_conn(db_conf):
	conn_string = "{}://{}:{}@{}:{}/{}".format(
		db_conf['type'],
		db_conf['db_redis_user'],
		db_conf['db_redis_password'],
		db_conf['host'],
		db_conf['port'],
		db_conf['db']
	)

	return create_engine(conn_string)

def log_share_attempt(db, redis_log_table, message):
	try:
		result = db.execute(
			redis_log_table.insert().values(
				message=message
			)
		)

		primary_key = result.inserted_primary_key
		return primary_key
	except Exception as e:
		print "had trouble inserting redis log:", e
		return None

	return None

def add_redis_log_result(db, redis_log_table, log_id, result):
	try:
		 db.execute(
			redis_log_table.update().where(
				redis_log_table.c.id == log_id
			).values(
				db_result=result
			)
		)
	except Exception as e:
		print "had trouble updating redis log:", e

def add_new_share(db, shares_table, new_share):
	try:
		# get into a format that sqlalchemy will like
		insert_row = {
			"ownerid": new_share['ownerid'],
			"shareid": new_share['shareid']
		}

		# insert the rows to the shares table
		db.execute(
			shares_table.insert().values(
				insert_row
			)
		)
	except Exception as e:
		print "had trouble inserting new share:", e
		if hasattr(e, "message"):
			return e.message
		else:
			return "DB insertion failed, couldn't get the exception message"

	return True

def parse_share(data):
	if valid_share.match(data):
		res = valid_share.search(data)
		ownerid = int(res.group("from"))
		shareid = int(res.group("to"))

		# make sure someone isn't sharing with themselves
		if ownerid != shareid:
			return {
				"ownerid": ownerid,
				"shareid": shareid
			}

	return False

def main():
	# get our config
	conf = get_conf()
	redis_conf = conf['redis']
	db_conf = conf['sql']
	reg_sleep = 1 # sleep for 1 seconds between channel reads
	short_sleep = .001 # shorter sleep time for when we received messages previously

	# get DB connection objects
	redis = create_redis_conn(redis_conf)
	db = create_db_conn(db_conf)

	# do some sick reflection bc laziness
	meta = MetaData()
	meta.reflect(bind=db)
	shares_table = meta.tables['shares']
	redis_log_table = meta.tables['redis_logs']

	# get a pubsub object and subscribe to our channel
	try:
		p = redis.pubsub(ignore_subscribe_messages=True)
		p.subscribe(redis_conf['channel'])
	except Exception:
		print "issue subscribing to {}".format(redis_conf['channel'])
		return -1

	# keep checking messages forever and ever
	while True:
		# check for data, process if it's a message
		message = p.get_message()
		if message and message['type'] == "message":
			# log the attempt
			log_id = log_share_attempt(db, redis_log_table, message['data'])

			# validate the share value and get a dict of it
			new_share = parse_share(message['data'])

			# if we got a valid new_share add it to the DB
			if new_share:
				add_result = add_new_share(db, shares_table, new_share)
				if not isinstance(add_result, str):
					print "retrieved and added new shares successfully"
					db_result = "success"
				else:
					print "problem adding new shares :("
					db_result = add_result
			else:
				db_result = "invalid share (failed before reaching DB)"

			# log what happened after parsing and trying to insert this message
			add_redis_log_result(db, redis_log_table, log_id, db_result)

			# sleep before reading again. since we just read a message, don't sleep so long
			sleep(short_sleep)

		# we didn't get any messages this time, sleep for regular amount
		sleep(reg_sleep)

	return 0

if __name__ == "__main__":
	exit(main())
