from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from Utils.json_encoder import GenericJsonEncoder
from flask_mail import Mail, Message
from threading import Thread
from app_start_helper import mail
import requests
from Utils.emo_icons_to_strings import emo_icons_to_strings

from Utils.chatgpt_api_utils.summarise_using_chatgpt import summarise_using_chatgpt
from Utils.cohere_utils.summarise_using_cohere import summarise_using_cohere

comments_llm_questioning_blueprint = Blueprint('comments_llm_questioning_blueprint', __name__)

@comments_llm_questioning_blueprint.route('/api/comments-llm-questioning', methods=['POST'])
def comments_llm_questioning():
    payload = request.data
    payload = json.loads(payload)

    if payload['llmModel'] == 'chatGpt':
        reply = summarise_using_chatgpt(payload['top10ShuffledComments'], payload['emoIcon'])
    elif payload['llmModel'] == 'cohere':
        reply = summarise_using_cohere(payload['top10ShuffledComments'], payload['emoIcon'])
    else:
        reply = summarise_using_chatgpt(payload['top10ShuffledComments'], payload['emoIcon'])

    operation_response = {
        "operation_success": True,
        "responsePayload": {
            'llmGptReply': reply
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
