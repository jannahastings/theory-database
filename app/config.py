
import os
import secrets
secret_key = secrets.token_hex(16) #random string 


if os.environ.get("FLASK_ENV")=='development':
    SECRET_KEY = secret_key
    # SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
else:
    SECRET_KEY = secret_key
    # SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

INDEX_DIR="/data/theory-database/index/"
