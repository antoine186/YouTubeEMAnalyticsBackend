
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

get_previous_linking_blueprint = Blueprint('get_previous_linking_blueprint', __name__)

@get_previous_linking_blueprint.route('/api/get-previous-linking', methods=['POST'])
def get_previous_linking():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    get_linking_result = 'SELECT search_schema.get_linking_result(:user_id)'

    linking_result = db.session.execute(text(get_linking_result), {'user_id': user_id[0][0]}).fetchall()

    if linking_result[0][0] != None:
        linking_result = json.loads(linking_result[0][0])
    else:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response

    operation_response = {
        "operation_success": True,
        "responsePayload": {
            "linking_result": linking_result
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response

