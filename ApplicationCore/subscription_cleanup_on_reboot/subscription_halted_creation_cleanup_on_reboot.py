from models.payment_schema.stripe_subscription_creation_status import StripeSubscriptionCreationStatus
from sqlalchemy import text
from app_start_helper import db
import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key

def subscription_halted_creation_cleanup_on_reboot():
    all_unfinished_stripe_subscription_creations = StripeSubscriptionCreationStatus.query.all()

    for unfinished_stripe_subscription_creation in all_unfinished_stripe_subscription_creations:
        get_username = 'SELECT user_schema.get_username(:user_id)'
        username = db.session.execute(text(get_username), {'user_id': unfinished_stripe_subscription_creation.user_id}).fetchall()

        stripe_customer_search_result = stripe.Customer.search(
            query="email:'{}'".format(username[0][0]),
        )

        if len(stripe_customer_search_result._last_response.data['data']) > 0:
            subscription_mini_list_for_user = stripe.Subscription.list(customer=stripe_customer_search_result._last_response.data['data'][0]['id'], limit=1)

            if len(subscription_mini_list_for_user._last_response.data['data']) > 0:
                for subscription_data in subscription_mini_list_for_user._last_response.data['data']:
                    if subscription_data['status'] != 'active' and subscription_data['status'] != 'trialing':
                        stripe.Subscription.cancel(subscription_data['id'])

        delete_stripe_subscription_creation_status_sp = 'CALL payment_schema.delete_stripe_subscription_creation_status(:user_id)'

        db.session.execute(text(delete_stripe_subscription_creation_status_sp), {'user_id': unfinished_stripe_subscription_creation.user_id})
        db.session.commit()


    """
    for unfinished_stripe_subscription_creation in all_unfinished_stripe_subscription_creations:
        delete_stripe_subscription_creation_status_sp = 'CALL payment_schema.delete_stripe_subscription_creation_status(:user_id)'

        db.session.execute(text(delete_stripe_subscription_creation_status_sp), {'user_id': user_id[0][0]})
        db.session.commit()
    """