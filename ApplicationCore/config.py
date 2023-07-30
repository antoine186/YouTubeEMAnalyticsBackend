import os
import psycopg2

SECRET_KEY = os.urandom(32)

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

stripe_api_key = 'sk_test_51MyG0LFAAs2DFWSVpgT2ghJhCoQnlrO1Y3F29CHsGJkpyaZ8Qo5b7V2hRn8cLmqj4pWmYAI0eLKGWBZubjDsn8cw00or9QmyMd'
# stripe_api_key = 'pk_live_51MyG0LFAAs2DFWSVTtM2eTdG4mfJiRudWfsLF0ilmaQwOOZ2nufVf5SlkLxMVFV5d5WbPAfG948Jav5TedJIvSS800aqnFMq5r'

# This is for prod
# stripe_api_key = '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'

# Connect to the database
# postgres://{user}:{password}@{hostname}:{port}/{database-name}
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:login123@localhost:5432/postgres'

# This is for prod
# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Emocritical186@database-3.ccigqpo72mbx.us-east-2.rds.amazonaws.com:5432/postgres'

# Turn off the Flask-SQLAlchemy event system and warning
SQLALCHEMY_TRACK_MODIFICATIONS = False
