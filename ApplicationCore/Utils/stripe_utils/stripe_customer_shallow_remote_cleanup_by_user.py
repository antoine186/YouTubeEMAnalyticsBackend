from app_start_helper import db
import stripe
from sqlalchemy import text

def stripe_customer_shallow_remote_cleanup_by_user(user_id):
    get_username = 'SELECT user_schema.get_username(:user_id)'
    username = db.session.execute(text(get_username), {'user_id': user_id}).fetchall()

    if username[0][0] != None:
        stripe_customer_search_result = stripe.Customer.search(
            query="email:'{}'".format(username[0][0]),
        )

        if len(stripe_customer_search_result._last_response.data['data']) > 0:
            existing_stripe_customer_id = stripe_customer_search_result._last_response.data['data'][0]['id']
            stripe.Customer.delete(existing_stripe_customer_id)

        delete_stripe_customer_creation_status_sp = 'CALL payment_schema.delete_stripe_customer_creation_status(:user_id)'

        db.session.execute(text(delete_stripe_customer_creation_status_sp), {'user_id': user_id})
        db.session.commit()
