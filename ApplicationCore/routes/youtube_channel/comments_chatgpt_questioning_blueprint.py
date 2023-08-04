from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from Utils.json_encoder import GenericJsonEncoder
from flask_mail import Mail, Message
from threading import Thread
from app_start_helper import mail
import requests
from Utils.chatgpt_api_utils.summarise_using_chatgpt import summarise_using_chatgpt
from Utils.emo_icons_to_strings import emo_icons_to_strings

comments_chatgpt_questioning_blueprint = Blueprint('comments_chatgpt_questioning_blueprint', __name__)

@comments_chatgpt_questioning_blueprint.route('/api/comments-chatgpt-questioning', methods=['POST'])
def comments_chatgpt_questioning():
    payload = request.data
    payload = json.loads(payload)

    reply = summarise_using_chatgpt(payload['top10ShuffledComments'], payload['emoIcon'])

    operation_response = {
        "operation_success": True,
        "responsePayload": {
            'ChatGptReply': reply
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
