from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

check_still_searching_blueprint = Blueprint('check_still_searching_blueprint', __name__)

@check_still_searching_blueprint.route('/api/check_still_searching', methods=['POST'])
def check_still_searching():
    try:
        payload = request.data
        payload = json.loads(payload)

        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

        check_still_searching = 'SELECT search_schema.check_still_searching(:user_id)'

        still_searching = db.session.execute(text(check_still_searching), {'user_id': user_id[0][0]}).fetchall()
        
        if still_searching[0][0] != None:
            operation_response = {
                "operation_success": True,
                "responsePayload": {
                    "still_searching": still_searching[0][0]
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
    
    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
