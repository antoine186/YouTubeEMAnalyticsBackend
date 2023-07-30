from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

password_reset_blueprint = Blueprint('password_reset_blueprint', __name__)

@password_reset_blueprint.route('/api/password_reset', methods=['POST'])
def basic_account_create():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']['passwordResetAccountState']['payload']}).fetchall()

    match_password_reset_token = 'SELECT user_schema.match_password_reset_token(:user_id,:reset_token)'

    token_match = db.session.execute(text(match_password_reset_token), {'user_id': user_id[0][0], 'reset_token': payload['resetToken']}).fetchall()

    if token_match[0][0] == 1:
        update_password_sp = 'CALL user_schema.update_password(:user_id,:password)'

        db.session.execute(text(update_password_sp), {'user_id': user_id[0][0], 'password': payload['password']})

        db.session.commit()

        operation_response = {
            "operation_success": True,
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
    else:
        operation_response = {
            "operation_success": False,
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
