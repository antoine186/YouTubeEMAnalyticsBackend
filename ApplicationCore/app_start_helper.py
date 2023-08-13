from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sys
from DependenciesResources.containers import Container
from flask_mail import Mail, Message

from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

import openai

from apiclient.discovery import build

app = Flask(__name__)
app.config.from_object('config')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "noreply@emomachines.xyz"
app.config['MAIL_PASSWORD'] = "jdztxwrikhatwrcn"

mail = Mail(app)

CORS(app, supports_credentials=True)

db = SQLAlchemy()
migrate = Migrate(app, db)

scheduler = BackgroundScheduler()

container = Container()
container.wire(modules=[sys.modules[__name__]])

paths = Container.resources_path()
nn = Container.pipeline_neural_network()
#keyword_extractor_nn = Container.keyword_extractor_neural_network()
model_max_characters_allowed = 600
model_max_words_allowed = 300

DEVELOPER_KEY = "AIzaSyAodk67-ODzonfyWsYp4gnuasgxAm0cNJI"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                        developerKey = DEVELOPER_KEY)

# Emotional Machines API Key
# rapidapi_key = "2b15b711e0msh4c5b33d95d9470dp1d558bjsn4dc897e8f19f"

# antoine.tian@emomachines.xyz API Key
rapidapi_key = "ddf2e48d8emsh02dbd4229cc9355p1a54eajsn7072e5a726e3"

openai.api_key = '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'

# Switch variables below between prod and debug

# !!! THIS IS THE MASTER SWITCH !!!
debug_switched_on = False

chat_gpt_testing = False

number_of_seconds_prod = 7200
number_of_seconds_debug = 15

# Each page represents 20 comments
number_of_comment_pages_prod = 50
number_of_comment_pages_debug = 10

stripe_api_key_prod = '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'
stripe_api_key_debug = 'sk_test_51MyG0LFAAs2DFWSVpgT2ghJhCoQnlrO1Y3F29CHsGJkpyaZ8Qo5b7V2hRn8cLmqj4pWmYAI0eLKGWBZubjDsn8cw00or9QmyMd'

SQLALCHEMY_DATABASE_URI_PROD = 'postgresql://postgres:Emocritical186@database-3.ccigqpo72mbx.us-east-2.rds.amazonaws.com:5432/postgres'
SQLALCHEMY_DATABASE_URI_DEBUG = 'postgresql://postgres:login123@localhost:5432/postgres'
