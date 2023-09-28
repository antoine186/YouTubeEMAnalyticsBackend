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

        if stripe_subscription_id[0][0] != None:
            retrieved_subscription = stripe.Subscription.retrieve(
                stripe_subscription_id[0][0],
            )

            if retrieved_subscription.status != 'active' and retrieved_subscription.status != 'trialing':
                delete_subscription_sp = 'CALL payment_schema.delete_subscription(:internal_stripe_customer_id)'
                db.session.execute(text(delete_subscription_sp), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]})

                db.session.commit()

            latest_invoice = stripe.Invoice.retrieve(
                retrieved_subscription.latest_invoice,
            )

            if latest_invoice.payment_intent != None:
                payment_or_setup_intent = stripe.PaymentIntent.retrieve(
                    latest_invoice.payment_intent,
                )
            else:
                get_stripe_subscription_client_secret = 'SELECT payment_schema.get_stripe_subscription_client_secret(:user_id)'
                stripe_subscription_client_secret = db.session.execute(text(get_stripe_subscription_client_secret), {'user_id': user_id[0][0]}).fetchall()

                stripe_subscription_client_secret_list = stripe_subscription_client_secret[0][0].split("_secret_")

                payment_or_setup_intent = stripe.SetupIntent.retrieve(
                    stripe_subscription_client_secret_list[0],
                )

            operation_response = {
                "operation_success": True,
                "responsePayload": {
                    "stripe_subscription_id": retrieved_subscription.id,
                    "client_secret": payment_or_setup_intent.client_secret,
                    "subscription_status": retrieved_subscription.status
                },
                "error_message": "" 
            }
            response = make_response(json.dumps(operation_response))
            return response
        else:
            operation_response = {
                "operation_success": False,
                "responsePayload": {
                },
                "error_message": "no_subscription_found" 
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
