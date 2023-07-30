# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key

from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

delete_subscription_blueprint = Blueprint('setupintent_creation_blueprint', __name__)

@delete_subscription_blueprint.route('/api/delete_subscription', methods=['POST'])
def delete_subscription():
    payload = request.data
    payload = json.loads(payload)

    try:
        subscription_to_delete = stripe.Subscription.retrieve(
            payload['stripeSubscriptionId'],
        )

        last_cancelled_invoice = stripe.Invoice.retrieve(
            subscription_to_delete.latest_invoice,
        )

        deleted_subscription = stripe.Subscription.delete(
            payload['stripeSubscriptionId'],
            prorate=True
        )

        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

        get_internal_stripe_customer_id = 'SELECT payment_schema.get_internal_stripe_customer_id(:user_id)'

        internal_stripe_customer_id = db.session.execute(text(get_internal_stripe_customer_id), {'user_id': user_id[0][0]}).fetchall()

        delete_subscription_sp = 'CALL payment_schema.delete_subscription(:internal_stripe_customer_id)'

        db.session.execute(text(delete_subscription_sp), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]})

        db.session.commit()

    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": "Subscription deletion failed" 
        }
        response = make_response(json.dumps(operation_response))
        return response
    
    try:
        customer_invoice_list = stripe.InvoiceItem.list(
            customer=deleted_subscription.customer,
            pending=True
        )

        amount_to_refund = -customer_invoice_list.data[0].amount

        stripe.InvoiceItem.delete(
            customer_invoice_list.data[0].id,
        )

        stripe.Refund.create(payment_intent=last_cancelled_invoice.payment_intent, amount=amount_to_refund)
    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": "Refund failed" 
        }
        response = make_response(json.dumps(operation_response))
        return response
    
    operation_response = {
        "operation_success": True,
        "responsePayload": {
        },
        "error_message": ""
    }
    response = make_response(json.dumps(operation_response))
    return response
