#from . import api
from flask_restplus import Resource, Namespace, reqparse
from time import sleep
from .utils import random_sleep_time, flip_coin, random_data, random_username
from json import dumps

ns = Namespace('creds', description='Fetches credentials from secret management (Vault)')

@ns.route('/')
class Creds(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument(
		'cred',
		type=unicode,
		help='Must give name of credential you want',
		location='args',
	)

	@ns.expect(parser)
	def get(self):
		args = self.parser.parse_args()
		creds = {}
		sleep(random_sleep_time(30, 100))

		#if they give redis, reject them
		if "redis" in args['cred'].lower():
			return "not implemented yet"
		#otherwise, 90% of the time return a random username:password combo
		elif flip_coin(weight=.15):
			#get a random username and password, put it into a dict and return json
			username = random_username()
			password = random_data()
			creds = {
				"username": username,
				"password": password
			}

		#the other half, print out our favorite little string as the password ;)
		#just google it
		else:
			creds = {
				"username": "jon_sudano",
				"password": "QbgGIy3kKiM"
			}

		return dumps(creds)
