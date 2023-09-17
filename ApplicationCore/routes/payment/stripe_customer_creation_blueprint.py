# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key

from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

stripe_customer_creation_blueprint = Blueprint('stripe_customer_creation_blueprint', __name__)

@stripe_customer_creation_blueprint.route('/api/stripe-customer-create', methods=['POST'])
def stripe_customer_create():
    payload = request.data
    payload = json.loads(payload)

    try:
        # Commented out because don't need this as it's cleaned up in stripe_customer_shallow_remote_cleanup()
        #check_stripe_customer_creation_status = 'SELECT payment_schema.check_stripe_customer_creation_status(:user_id)'
        #stripe_customer_creation_status_id = db.session.execute(text(check_stripe_customer_creation_status), {'user_id': user_id[0][0]}).fetchall()

        #stripe_customer_creation_status_id != None:
            #

        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['accountCreationData']['emailAddress']}).fetchall()

        add_stripe_customer_creation_status_sp = 'CALL payment_schema.add_stripe_customer_creation_status(:user_id,:status)'

        db.session.execute(text(add_stripe_customer_creation_status_sp), {'user_id': user_id[0][0], 'status': 'true'})
        db.session.commit()

        new_stripe_customer = stripe.Customer.create(
        email=payload['accountCreationData']['emailAddress'],
        name=payload['accountCreationData']['firstName'] + " " + payload['accountCreationData']['lastName'],
        )

        # DB operations here
        add_stripe_customer_sp = 'CALL payment_schema.add_stripe_customer(:user_id,:stripe_customer_id)'

        db.session.execute(text(add_stripe_customer_sp), {'user_id': user_id[0][0], 'stripe_customer_id': new_stripe_customer.id})
        db.session.commit()

        delete_stripe_customer_creation_status_sp = 'CALL payment_schema.delete_stripe_customer_creation_status(:user_id)'

        db.session.execute(text(delete_stripe_customer_creation_status_sp), {'user_id': user_id[0][0]})
        db.session.commit()

        delete_basic_account_create_stripe_customer_id_status_sp = 'CALL payment_schema.delete_basic_account_create_stripe_customer_id_status(:user_id)'

        db.session.execute(text(delete_basic_account_create_stripe_customer_id_status_sp), {'user_id': user_id[0][0]})
        db.session.commit()

        operation_response = {
            "operation_success": True,
            "responsePayload": {
                "stripe_customer_id": new_stripe_customer.id
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
    