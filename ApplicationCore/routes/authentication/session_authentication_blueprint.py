from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

session_authentication_blueprint = Blueprint('session_authentication_blueprint', __name__)

@session_authentication_blueprint.route('/api/session-validate', methods=['POST'])
def session_check():
    payload = request.data
    payload = json.loads(payload)

    session_confirmed = db.session.execute(text('SELECT user_schema.check_session_active(:user_id,:secret_token_1,:secret_token_2)'), 
                                           {'user_id': payload['userId'], 'secret_token_1': payload['secretToken1'], 'secret_token_2': payload['secretToken2']}).fetchall()
    
    if session_confirmed[0][0] == 1:
        return json.dumps(True)
    else:
        return json.dumps(False)
