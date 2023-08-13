from flask import Blueprint, request, make_response
from sqlalchemy import text
from models.user_safe_view import UserSafeView
from app_start_helper import db, debug_switched_on, number_of_seconds_prod, number_of_seconds_debug
from Utils.create_secret_token import create_secret_token
import json
from datetime import datetime

authentication_blueprint = Blueprint('authentication_blueprint', __name__)

@authentication_blueprint.route('/api/auth-login', methods=['POST'])
def login():
    payload = request.data
    payload = json.loads(payload)

    if debug_switched_on:
        seconds = number_of_seconds_debug
    else:
        seconds = number_of_seconds_prod

    credential_confirmed = db.session.execute(text('SELECT user_schema.check_username_password(:username,:password)'), {'username': payload['username'], 'password': payload['password']}).fetchall()

    if credential_confirmed[0][0] == 1:
        user_safe_view = UserSafeView.query.filter_by(username = payload['username']).first()

        how_many_sessions_active = 'SELECT user_schema.how_many_sessions_active(:user_id)'
        how_many_sessions_active_result = db.session.execute(text(how_many_sessions_active), 
                                                        {'user_id': user_safe_view.user_id}).fetchall()
        
        if how_many_sessions_active_result[0][0] == 0:
            validated_user_id = user_safe_view.user_id
            secret_token_1 = create_secret_token()
            secret_token_2 = create_secret_token()

            now = datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M:%S")

            db.session.execute(text('CALL user_schema.add_user_session(:user_id,:secret_token_1,:secret_token_2,:creation_date)'),
                                {'user_id': validated_user_id, 'secret_token_1': secret_token_1, 'secret_token_2': secret_token_2, 'creation_date': now})

            db.session.commit()

            session_token = {
                'username': payload['username'],
                'user_id': validated_user_id,
                'secret_token_1': secret_token_1,
                'secret_token_2': secret_token_2
            }

            operation_response = {
                "operation_success": True,
                "responsePayload": {
                },
                "error_message": ""
            }

            response = make_response(json.dumps(operation_response))
            #response.set_cookie('user_session_cookie', json.dumps(session_token), max_age = seconds, samesite = None , secure = True, httponly = True)
            response.set_cookie('user_session_cookie', json.dumps(session_token), max_age = seconds, samesite = None , secure = False, httponly = False)
            # response.headers['Access-Control-Allow-Origin'] = 'http://localhost/'
            # response.headers['Access-Control-Allow-Origin'] = '*'
            # response.headers['Access-Control-Allow-Credentials'] = 'true'

        else:
            operation_response = {
                "operation_success": False,
                "responsePayload": {
                },
                "error_message": "one_session_already_active"
            }
            response = make_response(json.dumps(operation_response))

        return response

    operation_response = {
        "operation_success": False,
        "responsePayload": {
        },
        "error_message": "wrong_credentials"
    }
    response = make_response(json.dumps(operation_response))

    return response
