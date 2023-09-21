
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

delete_account_blueprint = Blueprint('delete_account_blueprint', __name__)

@delete_account_blueprint.route('/api/delete_account', methods=['POST'])
def delete_account():
    try:
        payload = request.data
        payload = json.loads(payload)

        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['emailAddress']}).fetchall()

        delete_stripe_customer_creation_status_sp = 'CALL payment_schema.delete_stripe_customer_creation_status(:user_id)'

        db.session.execute(text(delete_stripe_customer_creation_status_sp), {'user_id': user_id[0][0]})
        db.session.commit()

        delete_basic_account_create_stripe_customer_id_status_sp = 'CALL payment_schema.delete_basic_account_create_stripe_customer_id_status(:user_id)'

        db.session.execute(text(delete_basic_account_create_stripe_customer_id_status_sp), {'user_id': user_id[0][0]})
        db.session.commit()

        delete_address_sp = 'CALL user_schema.delete_address(:user_id)'

        db.session.execute(text(delete_address_sp), {'user_id': user_id[0][0]})
        db.session.commit()

        if payload['deleteUserSessionData'] == True:
            delete_password_token_sp = 'CALL user_schema.delete_password_token(:user_id)'

            db.session.execute(text(delete_password_token_sp), {'user_id': user_id[0][0]})
            db.session.commit()

            delete_all_user_sessions_sp = 'CALL user_schema.delete_all_user_sessions(:user_id)'

            db.session.execute(text(delete_all_user_sessions_sp), {'user_id': user_id[0][0]})
            db.session.commit()

        delete_user_sp = 'CALL user_schema.delete_user(:user_id)'

        db.session.execute(text(delete_user_sp), {'user_id': user_id[0][0]})
        db.session.commit()

        return json.dumps(True)
    except Exception as e:
        return json.dumps(False)
