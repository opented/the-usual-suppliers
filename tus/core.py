import logging

from flask import Flask
from flask.ext.assets import Environment

from tus import default_settings


logging.basicConfig(level=logging.DEBUG)

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('TUS_SETTINGS', silent=True)

assets = Environment(app)


