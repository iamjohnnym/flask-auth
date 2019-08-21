from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_praetorian import Praetorian

# Give us an ORM to work with
db = SQLAlchemy()
# Migrating database models for SQL Alchemy
migrate = Migrate()
# To allow services to communicate with this
cors = CORS()
# User Security
guard = Praetorian()
# Debugging Toolbar...(might be unneeded now that we don't use flask's
# frontend)
toolbar = DebugToolbarExtension()
