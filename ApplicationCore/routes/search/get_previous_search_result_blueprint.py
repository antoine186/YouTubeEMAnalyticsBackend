from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

get_previous_search_result_blueprint = Blueprint('get_previous_search_result_blueprint', __name__)

@get_previous_search_result_blueprint.route('/api/get-previous-search-result', methods=['POST'])
def get_previous_search_result():
    try:
        payload = request.data
        payload = json.loads(payload)

        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

        get_previous_search_result = 'SELECT search_schema.get_previous_search_result(:user_id)'

        previous_search_result_json = db.session.execute(text(get_previous_search_result), {'user_id': user_id[0][0]}).fetchall()
        
        if previous_search_result_json[0][0] != None:
            previous_search_result = json.loads(previous_search_result_json[0][0])
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
                "previous_search_result": previous_search_result
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
    
    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
