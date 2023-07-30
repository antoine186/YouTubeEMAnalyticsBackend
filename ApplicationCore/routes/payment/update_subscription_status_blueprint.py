
from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text

update_subscription_status_blueprint = Blueprint('update_subscription_status_blueprint', __name__)

@update_subscription_status_blueprint.route('/api/update_subscription_status', methods=['POST'])
def update_subscription_status():
    payload = request.data
    payload = json.loads(payload)

    update_stripe_subscription_status_sp = 'CALL payment_schema.update_stripe_subscription_status(:stripe_subscription_id,:stripe_subscription_status)'

    db.session.execute(text(update_stripe_subscription_status_sp), {'stripe_subscription_id': payload['stripeSubscriptionId'], \
                                                                     'stripe_subscription_status': payload['subscriptionStatus']})
    
    db.session.commit()

    return json.dumps(True)
