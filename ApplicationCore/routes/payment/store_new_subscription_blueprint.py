
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

store_new_subscription_blueprint = Blueprint('store_new_subscription_blueprint', __name__)

@store_new_subscription_blueprint.route('/api/store_new_subscription', methods=['POST'])
def store_new_subscription():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['emailAddress']}).fetchall()

    get_internal_stripe_customer_id = 'SELECT payment_schema.get_internal_stripe_customer_id(:user_id)'

    internal_stripe_customer_id = db.session.execute(text(get_internal_stripe_customer_id), {'user_id': user_id[0][0]}).fetchall()

    check_subscription_exists = 'SELECT payment_schema.check_subscription_exists(:internal_stripe_customer_id)'

    subscription_exists = db.session.execute(text(check_subscription_exists), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]}).fetchall()

    if subscription_exists[0][0] == 0:
        add_stripe_subscription_sp = 'CALL payment_schema.add_stripe_subscription(:stripe_subscription_id,:internal_stripe_customer_id,:stripe_subscription_status)'

        db.session.execute(text(add_stripe_subscription_sp), {'stripe_subscription_id': payload['stripeSubscriptionId'], 'internal_stripe_customer_id': \
                                                                internal_stripe_customer_id[0][0], 'stripe_subscription_status': payload['subscriptionStatus']})
        db.session.commit()

    return json.dumps(True)
