import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key

from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

retrieve_subscription_details_blueprint = Blueprint('retrieve_subscription_details_blueprint', __name__)

@retrieve_subscription_details_blueprint.route('/api/retrieve_subscription_details', methods=['POST'])
def retrieve_subscription_details():
    payload = request.data
    payload = json.loads(payload)

    try:
        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

        get_internal_stripe_customer_id = 'SELECT payment_schema.get_internal_stripe_customer_id(:user_id)'

        internal_stripe_customer_id = db.session.execute(text(get_internal_stripe_customer_id), {'user_id': user_id[0][0]}).fetchall()

        get_stripe_subscription_id = 'SELECT payment_schema.get_stripe_subscription_id(:internal_stripe_customer_id)'

        stripe_subscription_id = db.session.execute(text(get_stripe_subscription_id), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]}).fetchall()

        retrieved_subscription = stripe.Subscription.retrieve(
            stripe_subscription_id[0][0],
        )

        latest_invoice = stripe.Invoice.retrieve(
            retrieved_subscription.latest_invoice,
        )

        payment_intent = stripe.PaymentIntent.retrieve(
            latest_invoice.payment_intent,
        )

        operation_response = {
            "operation_success": True,
            "responsePayload": {
                "stripe_subscription_id": retrieved_subscription.id,
                "client_secret": payment_intent.client_secret,
                "subscription_status": retrieved_subscription.status
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
