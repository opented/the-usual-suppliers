
from tus.core import app

@app.route('/')
def index():
    return 'hello, world!'
