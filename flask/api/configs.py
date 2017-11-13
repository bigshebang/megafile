#from . import api
from flask_restplus import Resource, Namespace, reqparse
import urllib
from time import sleep
from .utils import random_sleep_time

ns = Namespace('configs', description='Fetches configs for servers, networking devices and appliances')

@ns.route('/')
class Configs(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument(
		'url',
		type=unicode,
		help='Must give URL to fetch config from',
		location='form',
	)

	@ns.expect(parser)
	def post(self):
		
		args = self.parser.parse_args()

		sleep(random_sleep_time())

		result = urllib.urlopen(args['url'])
		output = result.read().decode("utf-8", errors="replace")
		return output
