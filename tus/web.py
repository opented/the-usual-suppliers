from flask import render_template

from tus.core import app
from tus.aggregator import aggregate_request
from tus.util import * 


@app.route('/')
def index():
    state = aggregate_request()
    return render_template('index.html', state=state)
