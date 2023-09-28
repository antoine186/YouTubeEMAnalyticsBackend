import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key

from flask import Blueprint, request, make_response
import json
from app_start_helper import number_of_seconds_prod, number_of_seconds_debug
from sqlalchemy import text

session_configuration_data_blueprint = Blueprint('session_configuration_data_blueprint', __name__)

@session_configuration_data_blueprint.route('/api/session_configuration_data', methods=['POST'])
def session_configuration_data():
    try:
        operation_response = {
            "operation_success": True,
            "responsePayload": {
                "number_of_seconds_prod": number_of_seconds_prod,
                "number_of_seconds_debug": number_of_seconds_debug
            },
            "error_message": "" 
        }
        response = make_response(json.dumps(operation_response))
        return response
    
    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": "" 
        }
        response = make_response(json.dumps(operation_response))
        return response
