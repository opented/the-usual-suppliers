from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from tus.core import assets
from tus.web import app


manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))


@manager.command
def run(port):
    app.run(host='0.0.0.0', port=int(port), debug=app.debug)

if __name__ == "__main__":
    manager.run()
