from flask import Blueprint, request, make_response
from sqlalchemy import text
from models.user_safe_view import UserSafeView
from app_start_helper import db
from Utils.create_secret_token import create_secret_token
import json
from datetime import datetime

authentication_blueprint = Blueprint('authentication_blueprint', __name__)

@authentication_blueprint.route('/api/auth-login', methods=['POST'])
def login():
    payload = request.data
    payload = json.loads(payload)

    seconds = 7200

    credential_confirmed = db.session.execute(text('SELECT user_schema.check_username_password(:username,:password)'), {'username': payload['username'], 'password': payload['password']}).fetchall()

    if credential_confirmed[0][0] == 1:
        user_safe_view = UserSafeView.query.filter_by(username = payload['username']).first()
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

        response = make_response(json.dumps(True))
        response.set_cookie('user_session_cookie', json.dumps(session_token), max_age = seconds, samesite = None , secure = True, httponly = True)
        # response.headers['Access-Control-Allow-Origin'] = 'http://localhost/'
        # response.headers['Access-Control-Allow-Origin'] = '*'
        # response.headers['Access-Control-Allow-Credentials'] = 'true'

        return response

    response = make_response(json.dumps(False))
    return response
