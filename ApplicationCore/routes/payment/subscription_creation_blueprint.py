# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key

from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

subscription_creation_blueprint = Blueprint('subscription_creation_blueprint', __name__)

@subscription_creation_blueprint.route('/api/subscription_create', methods=['POST'])
def subscription_create():
    payload = request.data
    payload = json.loads(payload)

    customer_id = payload['stripeCustomerId']
    price_id = payload['priceId']
    user_session_validated = payload['userSessionValidated']

    try:
        '''
        #subscription_list = stripe.Subscription.list(customer = customer_id)
        subscription_list = stripe.Subscription.list()
  
        for i in range(len(subscription_list)):
            existing_subscription = subscription_list.data[i]
            if existing_subscription.status == 'incomplete':
                print('Deleted previous incomplete subscription')
                stripe.SubscriptionItem.delete(
                    existing_subscription.id,
                )'''
        
        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['emailAddress']}).fetchall()

        delete_stripe_subscription_creation_status_sp = 'CALL payment_schema.delete_stripe_subscription_creation_status(:user_id)'

        db.session.execute(text(delete_stripe_subscription_creation_status_sp), {'user_id': user_id[0][0]})
        db.session.commit()
        
        add_stripe_subscription_creation_status_sp = 'CALL payment_schema.add_stripe_subscription_creation_status(:user_id,:status)'

        db.session.execute(text(add_stripe_subscription_creation_status_sp), {'user_id': user_id[0][0], 'status': 'true'})
        db.session.commit()

        # Create the subscription. Note we're expanding the Subscription's
        # latest invoice and that invoice's payment_intent
        # so we can pass it to the front end to confirm the payment
        if user_session_validated:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': price_id,
                }],
                currency='usd',
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
            print('Create sub without free trial')
        else:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': price_id,
                }],
                currency='usd',
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['pending_setup_intent'],
                trial_period_days=7
            )
            print('Create sub with free trial')

        if user_session_validated:
            operation_response = {
                "operation_success": True,
                "responsePayload": {
                    "stripe_subscription_id": subscription.id,
                    "client_secret": subscription.latest_invoice.payment_intent.client_secret
                },
                "error_message": "" 
            }
        else:
            operation_response = {
                "operation_success": True,
                "responsePayload": {
                    "stripe_subscription_id": subscription.id,
                    "client_secret": subscription.pending_setup_intent.client_secret
                },
                "error_message": "" 
            }

        # Commented out because this is handled in storing new subscription
        #delete_stripe_subscription_creation_status_sp = 'CALL payment_schema.delete_stripe_subscription_creation_status(:user_id)'

        #db.session.execute(text(delete_stripe_subscription_creation_status_sp), {'user_id': user_id[0][0]})
        #db.session.commit()

        response = make_response(json.dumps(operation_response))
        return response

    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": str(e)
        }
        response = make_response(json.dumps(operation_response))
        return response
    