# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key

from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

setupintent_creation_blueprint = Blueprint('setupintent_creation_blueprint', __name__)

@setupintent_creation_blueprint.route('/api/setupintent_creation', methods=['POST'])
def create_setupintent():
    payload = request.data
    payload = json.loads(payload)

    customer_id = payload['stripeCustomerId']

    setupintent = stripe.SetupIntent.create(
        customer=customer_id,
        usage="off_session",
        payment_method_types=["bancontact", "card", "ideal"]
        )
    
    operation_response = {
        "operation_success": True,
        "responsePayload": {
            "client_secret": setupintent.client_secret
        },
        "error_message": "" 
    }
    response = make_response(json.dumps(operation_response))
    return response
