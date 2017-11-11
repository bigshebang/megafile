from flask_restplus import Api
from flask import Blueprint
from .configs import ns as configs_ns
from .creds import ns as creds_ns

blueprint = Blueprint('api', __name__)
#api = Api(blueprint)
api = Api(blueprint, version='1.0', title='Hermes', description='API to fetch internal resources')
#api = Api(version='1.0', title='Hermes', description='API to fetch internal resources')

api.add_namespace(configs_ns)
api.add_namespace(creds_ns)
#api.add_namespace(configs_ns, path='/configs')
#api.add_namespace(creds_ns, path='/creds')

