
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

delete_account_blueprint = Blueprint('delete_account_blueprint', __name__)

@delete_account_blueprint.route('/api/delete_account', methods=['POST'])
def delete_account():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['accountCreationData']['emailAddress']}).fetchall()

    delete_address = 'CALL user_schema.delete_address(:user_id)'

    db.session.execute(text(delete_address), {'user_id': user_id[0][0]})
    db.session.commit()

    delete_user = 'CALL user_schema.delete_user(:user_id)'

    db.session.execute(text(delete_user), {'user_id': user_id[0][0]})
    db.session.commit()

    return json.dumps(True)
