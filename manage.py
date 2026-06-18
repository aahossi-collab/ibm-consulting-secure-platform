import os

from flask_migrate import MigrateCommand
from flask_script import Manager

from app import create_app
from app.extensions import db

app = create_app(os.getenv("FLASK_ENV", "development"))
manager = Manager(app)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
