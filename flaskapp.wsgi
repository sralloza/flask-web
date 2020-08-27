#!/srv/residence/.venv/bin/python

activate_this = "/srv/residence/.venv/bin/activate_this.py"
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys

sys.path.insert(0, "/srv/residence/")
from app import app as application

application.secret_key = "secret key"
