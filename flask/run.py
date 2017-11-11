from flask import Flask, Blueprint
#from flask_restplus import Api
#from api import api
from api import blueprint as api
#from api.configs import ns as configs_namespace
#from api.creds import ns as creds_namespace

app = Flask(__name__)
#api = Api(version='1.0', title='Hermes', description='API to fetch internal resources')

def configure_app(flask_app):
	flask_app.config.from_pyfile('app.cfg')

def initialize_app(flask_app):
	configure_app(flask_app)

	flask_app.register_blueprint(api)

	#blueprint = Blueprint('api', __name__)
	#app.register_blueprint(api, url_prefix='/api')
	#blueprint = Blueprint('api', __name__, url_prefix='/api')
	#api.init_app(blueprint)
	#api.add_namespace(configs_namespace)
	#api.add_namespace(creds_namespace)
	#flask_app.register_blueprint(blueprint)

def main():
	initialize_app(app)
	app.run(host=app.config['HOST'], port=app.config['PORT'])
	#app.run(port=8080)

if __name__ == '__main__':
	main()

