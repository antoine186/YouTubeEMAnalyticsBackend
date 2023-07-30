# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key
from flask import redirect, request

from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

create_checkout_blueprint = Blueprint('create_checkout_blueprint', __name__)

@create_checkout_blueprint.route('/api/create_checkout', methods=['POST'])
def create_checkout():
    payload = request.data
    payload = json.loads(payload)

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1NAOSKFAAs2DFWSVg8YjUb6N',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='https://emomachines.xyz' + '?success=true',
            cancel_url='https://emomachines.xyz' + '?canceled=true',
        )
    except Exception as e:
        return str(e)

    # return redirect(checkout_session.url, code=303)

    operation_response = {
        "operation_success": True,
        "responsePayload": {
            "checkout_url": checkout_session.url
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
