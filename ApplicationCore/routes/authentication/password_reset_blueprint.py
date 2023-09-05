from flask import Blueprint, request, make_response
import json
from app_start_helper import db, mail
from sqlalchemy import text
from Utils.create_secret_token import create_secret_token
from flask_mail import Mail, Message
from threading import Thread

password_reset_blueprint = Blueprint('password_reset_blueprint', __name__)

@password_reset_blueprint.route('/api/password_reset', methods=['POST'])
def password_reset():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']['passwordResetAccountState']['payload']}).fetchall()

    count_password_reset_tokens_for_user = 'SELECT user_schema.count_password_reset_tokens_for_user(:user_id)'

    password_reset_tokens_for_user_count = db.session.execute(text(count_password_reset_tokens_for_user), {'user_id': user_id[0][0]}).fetchall()

    if password_reset_tokens_for_user_count[0][0] == 0:

        password_token = create_secret_token()

        add_password_token_sp = 'CALL user_schema.add_password_token(:user_id,:password_reset_token)'

        db.session.execute(text(add_password_token_sp), {'user_id': user_id[0][0], 'password_reset_token': password_token})

        db.session.commit()

        msg = Message()
        msg.subject = "Password Reset for your Emotional Machines Account"
        msg.recipients = [payload['username']['passwordResetAccountState']['payload']]
        msg.sender = 'noreply@emomachines.xyz'
        msg.body = 'Your password reset token is ' + password_token +  '.'

        Thread(target=mail.send(msg)).start()

        operation_response = {
            "operation_success": False,
            "error_message": "reset_token_was_cleared_for_user"
        }
        response = make_response(json.dumps(operation_response))
        return response

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
