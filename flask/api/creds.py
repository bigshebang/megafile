#from . import api
from flask_restplus import Resource, Namespace

ns = Namespace('creds', description='Fetches credentials from secret management (Vault)')

#configs = ns.model('Configs'

@ns.route('/')
class Creds(Resource):
	def get(self):
		return 'this is the creds endpoint'
