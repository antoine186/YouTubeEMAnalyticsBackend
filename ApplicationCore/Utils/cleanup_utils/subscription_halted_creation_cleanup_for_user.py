from app_start_helper import db
from sqlalchemy import text
import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key

def subscription_halted_creation_cleanup_for_user(user_id):
    get_username = 'SELECT user_schema.get_username(:user_id)'
    username = db.session.execute(text(get_username), {'user_id': user_id}).fetchall()

    stripe_customer_search_result = stripe.Customer.search(
        query="email:'{}'".format(username[0][0]),
    )

    if len(stripe_customer_search_result._last_response.data['data']) > 0:
        subscription_mini_list_for_user = stripe.Subscription.list(customer=stripe_customer_search_result._last_response.data['data'][0]['id'], limit=100)

        for subscription_data in subscription_mini_list_for_user.auto_paging_iter():
            if subscription_data['status'] != 'active' and subscription_data['status'] != 'trialing':
                stripe.Subscription.cancel(subscription_data['id'])

    delete_stripe_subscription_creation_status_sp = 'CALL payment_schema.delete_stripe_subscription_creation_status(:user_id)'

    db.session.execute(text(delete_stripe_subscription_creation_status_sp), {'user_id': user_id})
    db.session.commit()
