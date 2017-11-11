#from . import api
from flask_restplus import Resource, Namespace, fields, reqparse
import urllib

ns = Namespace('configs', description='Fetches configs for servers, networking devices and appliances')

#configs = ns.model('Configs', {
#	'url': fields.String(required=False, description='The URL to fetch')
#})

@ns.route('/')
class Configs(Resource):
	@ns.doc('fetch_document')
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument(
			'url',
			type=unicode,
			help='Must give URL to fetch config from',
			location='form',
		)
		args = parser.parse_args()

		print "we got:",
		print args
		result = urllib.urlopen(args['url'])
		output = result.read().decode("utf-8", errors="replace")
		print "output: '%s'" % output
		return output
