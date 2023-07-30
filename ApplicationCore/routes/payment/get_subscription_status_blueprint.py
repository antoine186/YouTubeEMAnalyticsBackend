
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

get_subscription_status_blueprint = Blueprint('get_subscription_status_blueprint', __name__)

@get_subscription_status_blueprint.route('/api/get-subscription-status', methods=['POST'])
def get_subscription_status():
    payload = request.data
    payload = json.loads(payload)

    get_stripe_subscription_status = 'SELECT payment_schema.get_stripe_subscription_status(:stripe_subscription_id)'

    stripe_subscription_status = db.session.execute(text(get_stripe_subscription_status), {'stripe_subscription_id': payload['stripeSubscriptionId']}).fetchall()

    operation_response = {
        "operation_success": True,
        "responsePayload": {
            "stripe_subscription_status": stripe_subscription_status[0][0]
        },
        "error_message": "" 
    }
    response = make_response(json.dumps(operation_response))
    return response
