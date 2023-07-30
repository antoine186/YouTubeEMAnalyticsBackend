
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from Utils.create_secret_token import create_secret_token
from flask_mail import Mail, Message
from app_start_helper import mail
from threading import Thread

forgot_password_blueprint = Blueprint('forgot_password_blueprint', __name__)

@forgot_password_blueprint.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()
    
    if user_id[0][0] == None:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": "Account does not exist" 
        }
        response = make_response(json.dumps(operation_response))
        return response

    delete_password_token_sp = 'CALL user_schema.delete_password_token(:user_id)'

    db.session.execute(text(delete_password_token_sp), {'user_id': user_id[0][0]})

    db.session.commit()

    password_token = create_secret_token()

    add_password_token_sp = 'CALL user_schema.add_password_token(:user_id,:password_reset_token)'

    db.session.execute(text(add_password_token_sp), {'user_id': user_id[0][0], 'password_reset_token': password_token})

    db.session.commit()

    msg = Message()
    msg.subject = "Password Reset for your Emotional Machines Account"
    msg.recipients = [payload['username']]
    msg.sender = 'noreply@emomachines.xyz'
    msg.body = 'Your password reset token is ' + password_token +  '.'

    Thread(target=mail.send(msg)).start()

    operation_response = {
        "operation_success": True,
        "responsePayload": {
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
