from app_start_helper import db
from models.payment_schema.stripe_customer_creation_status import StripeCustomerCreationStatus
from sqlalchemy import text
import stripe
from ApplicationCore.config import stripe_api_key
stripe.api_key = stripe_api_key

def stripe_customer_shallow_remote_cleanup():
    """This has to run before purge_specific_user_by_email()
    
    This function is to purge an entire stripe customer when creation was halted halfway
    """
    all_unfinished_stripe_customer_creations = StripeCustomerCreationStatus.query.all()

    for unfinished_stripe_customer_creation in all_unfinished_stripe_customer_creations:
        get_username = 'SELECT user_schema.get_username(:user_id)'
        username = db.session.execute(text(get_username), {'user_id': unfinished_stripe_customer_creation.user_id}).fetchall()

        if username[0][0] != None:
            stripe_customer_search_result = stripe.Customer.search(
                query="email:'{}'".format(username[0][0]),
            )

            if len(stripe_customer_search_result._last_response.data['data']) > 0:
                existing_stripe_customer_id = stripe_customer_search_result._last_response.data['data'][0]['id']
                stripe.Customer.delete(existing_stripe_customer_id)

            delete_stripe_customer_creation_status_sp = 'CALL payment_schema.delete_stripe_customer_creation_status(:user_id)'

            db.session.execute(text(delete_stripe_customer_creation_status_sp), {'user_id': unfinished_stripe_customer_creation.user_id})
            db.session.commit()

            #print('Hello')
