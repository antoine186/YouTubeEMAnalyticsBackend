from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

get_previous_tagging_result_blueprint = Blueprint('get_previous_tagging_result_blueprint', __name__)

@get_previous_tagging_result_blueprint.route('/api/get-previous-tagging-result', methods=['POST'])
def get_previous_tagging_result():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    get_existing_tagging_query_id = 'SELECT search_schema.get_existing_tagging_query_id(:user_id,:tagging_query)'

    existing_tagging_query_id = db.session.execute(text(get_existing_tagging_query_id), {'user_id': user_id[0][0], 'tagging_query': payload['searchInput']}).fetchall()
    
    get_tagging_result = 'SELECT search_schema.get_tagging_result(:tagging_query_id)'

    previous_tagging_result = db.session.execute(text(get_tagging_result), {'tagging_query_id': existing_tagging_query_id[0][0]}).fetchall()

    if previous_tagging_result[0][0] != None:
        if previous_tagging_result[0][0] == 'No results':
            previous_tagging_result = previous_tagging_result[0][0]
        else:
            previous_tagging_result = json.loads(previous_tagging_result[0][0])

        operation_response = {
            "operation_success": True,
            "responsePayload": {
                "previous_search_result": previous_tagging_result
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
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
