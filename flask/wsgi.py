#!/usr/bin/env python
from flask import Flask, Blueprint
from api import blueprint as api

def create_app():
	app = Flask(__name__)
	app.register_blueprint(api)
	return app

app = create_app()

