
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

get_stripe_customer_id_blueprint = Blueprint('get_stripe_customer_id_blueprint', __name__)

@get_stripe_customer_id_blueprint.route('/api/get_stripe_customer_id', methods=['POST'])
def get_stripe_customer_id():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    get_internal_stripe_customer_id = 'SELECT payment_schema.get_internal_stripe_customer_id(:user_id)'

    internal_stripe_customer_id = db.session.execute(text(get_internal_stripe_customer_id), {'user_id': user_id[0][0]}).fetchall()

    get_stripe_customer_id = 'SELECT payment_schema.get_stripe_customer_id(:internal_stripe_customer_id)'

    stripe_customer_id = db.session.execute(text(get_stripe_customer_id), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]}).fetchall()

    operation_response = {
        "operation_success": True,
        "responsePayload": {
            "stripe_customer_id": stripe_customer_id[0][0]
        },
        "error_message": "" 
    }
    response = make_response(json.dumps(operation_response))
    return response
