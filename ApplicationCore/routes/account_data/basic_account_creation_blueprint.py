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

        add_basic_account_data_sp = 'CALL user_schema.add_basic_account_data(:primary_email,:password,:first_name,:last_name, \
            :date_of_birth,:telephone_number,:telephone_area_code)'
        
        get_user_id = 'SELECT user_schema.get_user_id(:username)'
        
        add_user_address_sp = 'CALL user_schema.add_user_address(:user_id,:country,:city,:street_1,:street_2,:zipcode,:state)'

        username_already_present = db.session.execute(text(check_username_present), {'username': payload['accountCreationData']['emailAddress']}).fetchall()

        if username_already_present[0][0] == 1:
            operation_response = {
                "operation_success": False,
                "error_message": "The account associated with your email already exists" 
            }
            response = make_response(json.dumps(operation_response))
            return response

        db.session.execute(text(add_basic_account_data_sp), {'first_name': payload['accountCreationData']['firstName'], 'last_name': payload['accountCreationData']['lastName'], \
                                                            'date_of_birth': payload['accountCreationData']['dateBirth'], 'primary_email': payload['accountCreationData']['emailAddress'], \
                                                                'telephone_number': payload['accountCreationData']['telephoneNumber'], 'telephone_area_code': payload['accountCreationData']['telephoneAreaCode'], \
                                                                    'password': payload['accountCreationData']['password']})
        
        db.session.commit()
        
        created_user_id = db.session.execute(text(get_user_id), {'username': payload['accountCreationData']['emailAddress']}).fetchall()

        if len(created_user_id) > 0:
            db.session.execute(text(add_user_address_sp), {'user_id': created_user_id[0][0], 'country': payload['accountCreationData']['selectedCountryName'], \
                                                        'city': payload['accountCreationData']['selectedCityName'], \
                                                            'street_1': payload['accountCreationData']['addressLine1'], 'street_2': payload['accountCreationData']['addressLine2'], \
                                                                'zipcode': payload['accountCreationData']['zipCode'], 'state': payload['accountCreationData']['selectedStateName']})
            db.session.commit()
        else:
            operation_response = {
                "operation_success": False,
                "error_message": "Something went wrong, please try again later" 
            }
            response = make_response(json.dumps(operation_response))
            return response

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
