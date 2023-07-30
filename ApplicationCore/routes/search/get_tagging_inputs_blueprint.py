from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

get_tagging_inputs_blueprint = Blueprint('get_tagging_inputs_blueprint', __name__)

@get_tagging_inputs_blueprint.route('/api/get-tagging-inputs', methods=['POST'])
def get_tagging_inputs():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    get_tagging_input = 'SELECT search_schema.get_tagging_input(:user_id)'

    tagging_input = db.session.execute(text(get_tagging_input), {'user_id': user_id[0][0]}).fetchall()

    if tagging_input[0][0] != None:
        operation_response = {
            "operation_success": True,
            "responsePayload": {
                "previous_tagging_input": json.loads(tagging_input[0][0])
        },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
    else:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": "No existing tagging input found" 
        }
        response = make_response(json.dumps(operation_response))
        return response
