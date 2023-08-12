from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

remove_session_blueprint = Blueprint('remove_session_blueprint', __name__)

@remove_session_blueprint.route('/api/remove-session', methods=['POST'])
def remove_session():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    delete_all_user_sessions_sp = 'CALL user_schema.delete_all_user_sessions(:user_id)'
    db.session.execute(text(delete_all_user_sessions_sp), {'user_id': user_id[0][0]})
    db.session.commit()

    operation_response = {
        "operation_success": True,
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
