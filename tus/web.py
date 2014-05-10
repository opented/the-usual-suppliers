from flask import render_template

from tus.core import app
from tus.aggregator import aggregate_request, contracts_request
from tus.util import * 


@app.route('/')
def index():
    state = aggregate_request()
    return render_template('index.html', state=state)


@app.route('/contracts')
def contracts():
    results = contracts_request()
    return render_template('contracts.html', results=results)
