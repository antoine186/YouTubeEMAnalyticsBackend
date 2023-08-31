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

from Utils.chatgpt_api_utils.elaborate_emo_using_chatgpt import elaborate_emo_using_chatgpt
from Utils.cohere_utils.elaborate_emo_using_cohere import elaborate_emo_using_cohere

comments_llm_emo_elaboration_blueprint = Blueprint('comments_llm_emo_elaboration_blueprint', __name__)

@comments_llm_emo_elaboration_blueprint.route('/api/comments-llm-emo-elaboration', methods=['POST'])
def comments_llm_emo_elaboration():
    payload = request.data
    payload = json.loads(payload)

    if payload['llmModel'] == 'chatGpt':
        reply = elaborate_emo_using_chatgpt(payload['top10ShuffledComments'], payload['emoIcon'])
    elif payload['llmModel'] == 'cohere':
        reply = elaborate_emo_using_cohere(payload['top10ShuffledComments'], payload['emoIcon'])
    else:
        reply = elaborate_emo_using_chatgpt(payload['top10ShuffledComments'], payload['emoIcon'])

    operation_response = {
        "operation_success": True,
        "responsePayload": {
            'emoElaborationllmGptReply': reply
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
