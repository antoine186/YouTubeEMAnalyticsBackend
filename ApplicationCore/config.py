import os
import psycopg2
#from app_start_helper import debug_switched_on, stripe_api_key_prod, stripe_api_key_debug, SQLALCHEMY_DATABASE_URI_DEBUG, SQLALCHEMY_DATABASE_URI_PROD

SECRET_KEY = os.urandom(32)

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# !!! THIS IS THE MASTER SWITCH !!!
debug_switched_on = True

if debug_switched_on:
    stripe_api_key = 'sk_test_51MyG0LFAAs2DFWSVpgT2ghJhCoQnlrO1Y3F29CHsGJkpyaZ8Qo5b7V2hRn8cLmqj4pWmYAI0eLKGWBZubjDsn8cw00or9QmyMd'
else:
    stripe_api_key = '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'

# Connect to the database
# postgres://{user}:{password}@{hostname}:{port}/{database-name}
if debug_switched_on:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost:5432/postgres'
else:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Emocritical186@database-1.ccigqpo72mbx.us-east-2.rds.amazonaws.com:5432/postgres'

# Turn off the Flask-SQLAlchemy event system and warning
SQLALCHEMY_TRACK_MODIFICATIONS = False
