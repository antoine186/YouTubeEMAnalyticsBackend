
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

get_subscription_id_blueprint = Blueprint('get_subscription_id_blueprint', __name__)

@get_subscription_id_blueprint.route('/api/get_subscription_id', methods=['POST'])
def get_subscription_id():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    get_internal_stripe_customer_id = 'SELECT payment_schema.get_internal_stripe_customer_id(:user_id)'

    internal_stripe_customer_id = db.session.execute(text(get_internal_stripe_customer_id), {'user_id': user_id[0][0]}).fetchall()

    get_stripe_subscription_id = 'SELECT payment_schema.get_stripe_subscription_id(:internal_stripe_customer_id)'

    stripe_subscription_id = db.session.execute(text(get_stripe_subscription_id), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]}).fetchall()

    if stripe_subscription_id[0][0] != None:
        operation_response = {
            "operation_success": True,
            "responsePayload": {
                "stripe_subscription_id": stripe_subscription_id[0][0]
            },
            "error_message": "" 
        }
    else:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": "" 
        }

    response = make_response(json.dumps(operation_response)) 
    return response
