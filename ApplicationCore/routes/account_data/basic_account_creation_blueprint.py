from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

basic_account_creation_blueprint = Blueprint('basic_account_creation_blueprint', __name__)

@basic_account_creation_blueprint.route('/api/basic-account-create', methods=['POST'])
def basic_account_create():
    payload = request.data
    payload = json.loads(payload)

    try:
        check_username_present = 'SELECT user_schema.check_username_present(:username)'

        add_basic_account_data_simplified_sp = 'CALL user_schema.add_basic_account_data_simplified(:primary_email,:password,:first_name,:last_name)'
        
        username_already_present = db.session.execute(text(check_username_present), {'username': payload['accountCreationData']['emailAddress']}).fetchall()

        if username_already_present[0][0] == 1:
            operation_response = {
                "operation_success": False,
                "error_message": "The account associated with your email already exists" 
            }
            response = make_response(json.dumps(operation_response))
            return response

        db.session.execute(text(add_basic_account_data_simplified_sp), {'first_name': payload['accountCreationData']['firstName'], 'last_name': payload['accountCreationData']['lastName'],
                                                            'primary_email': payload['accountCreationData']['emailAddress'], 'password': payload['accountCreationData']['password']})
        
        db.session.commit()

        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['accountCreationData']['emailAddress']}).fetchall()

        add_basic_account_create_stripe_customer_id_status_sp = 'CALL payment_schema.add_basic_account_create_stripe_customer_id_status(:user_id,:status)'

        db.session.execute(text(add_basic_account_create_stripe_customer_id_status_sp), {'user_id': user_id[0][0], 'status': 'true'})
        db.session.commit()

        operation_response = {
            "operation_success": True,
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
    
    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": str(e)
        }
        response = make_response(json.dumps(operation_response))
        return response
