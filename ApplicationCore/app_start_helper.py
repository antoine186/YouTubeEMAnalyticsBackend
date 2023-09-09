from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sys
from DependenciesResources.containers import Container
from flask_mail import Mail, Message

from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

import openai
import cohere

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

cohere_api_key = 'GDG3CKH8PDAoKuUsqnzKelIZHi5kiqrpKfTuVwzi'

cohere_client = cohere.Client(cohere_api_key)

youtube_comments_rapidapi_url = "https://yt-api.p.rapidapi.com/comments"

chatgpt4_rapidapi_url = "https://chatgpt-gpt4-ai-chatbot.p.rapidapi.com/ask"

# Switch variables below between prod and debug

# !!! THIS IS THE MASTER SWITCH !!! (THERE IS ANOTHER EXCEPTIONAL MASTER
# SWITCH IN CONFIG.PY TO PREVENT CIRCULAR IMPORTS)
debug_switched_on = True

# 1) LLM switches & params
llm_testing = False
chat_gpt_response_from_rapid_api = True

# 2) Session duration switches & params
number_of_seconds_prod = 7200
number_of_seconds_debug = 60 * 10

# 3) YouTube comments switches & params
# Each page represents 20 comments
number_of_comment_pages_prod = 50
number_of_comment_pages_debug = 10

# How many comments to generate video description
number_of_comments_to_generate_video_description = 50
number_of_comments_in_tranch_to_generate_video_description = 10

# 4) Purging on boot up switches & params
debug_purging_on = debug_switched_on
remote_stripe_entities_purging = True
