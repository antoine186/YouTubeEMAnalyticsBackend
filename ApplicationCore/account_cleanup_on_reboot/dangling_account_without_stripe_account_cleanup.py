from app_start_helper import db
from sqlalchemy import text
from models.payment_schema.basic_account_create_stripe_customer_id_status import BasicAccountCreateStripeCustomerIdStatus
import stripe

def dangling_account_without_stripe_account_cleanup():
    all_dangling_accounts_without_stripe_ids = BasicAccountCreateStripeCustomerIdStatus.query.all()

    for all_dangling_accounts_without_stripe_id in all_dangling_accounts_without_stripe_ids:
        get_username = 'SELECT user_schema.get_username(:user_id)'
        username = db.session.execute(text(get_username), {'user_id': all_dangling_accounts_without_stripe_id.user_id}).fetchall()

        # First delete stripe account if created but not recorded in DB
        if username[0][0] != None:
            stripe_customer_search_result = stripe.Customer.search(
                query="email:'{}'".format(username[0][0]),
            )

            if len(stripe_customer_search_result._last_response.data['data']) > 0:
                existing_stripe_customer_id = stripe_customer_search_result._last_response.data['data'][0]['id']
                stripe.Customer.delete(existing_stripe_customer_id)

            # Then delete entire account on backend
            # Delete from payment schema
            delete_stripe_customer_creation_status_sp = 'CALL payment_schema.delete_stripe_customer_creation_status(:user_id)'

            db.session.execute(text(delete_stripe_customer_creation_status_sp), {'user_id': all_dangling_accounts_without_stripe_id.user_id})
            db.session.commit()

            delete_stripe_subscription_creation_status_sp = 'CALL payment_schema.delete_stripe_subscription_creation_status(:user_id)'

            db.session.execute(text(delete_stripe_subscription_creation_status_sp), {'user_id': all_dangling_accounts_without_stripe_id.user_id})
            db.session.commit()

            get_internal_stripe_customer_id = 'SELECT payment_schema.get_internal_stripe_customer_id(:user_id)'
            internal_stripe_customer_id = db.session.execute(text(get_internal_stripe_customer_id), {'user_id': all_dangling_accounts_without_stripe_id.user_id}).fetchall()

            # Can simply delete subscription in backend because deleting the stripe customer will delete the corresponding subscriptions
            if internal_stripe_customer_id[0][0] != None:
                delete_subscription_sp = 'CALL payment_schema.delete_subscription(:internal_stripe_customer_id)'

                db.session.execute(text(delete_subscription_sp), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]})
                db.session.commit()

                delete_stripe_customer_sp = 'CALL payment_schema.delete_stripe_customer(:user_id)'

                db.session.execute(text(delete_stripe_customer_sp), {'user_id': all_dangling_accounts_without_stripe_id.user_id})
                db.session.commit()

            # Delete from logging schema
            delete_all_login_log_entries_for_users_sp = 'CALL logging_schema.delete_all_login_log_entries_for_users(:user_id)'

            db.session.execute(text(delete_all_login_log_entries_for_users_sp), {'user_id': all_dangling_accounts_without_stripe_id.user_id})
            db.session.commit()

            # Delete from user schema
            delete_address_sp = 'CALL user_schema.delete_address(:user_id)'

            db.session.execute(text(delete_address_sp), {'user_id': all_dangling_accounts_without_stripe_id.user_id})
            db.session.commit()

            delete_password_token_sp = 'CALL user_schema.delete_password_token(:user_id)'

            db.session.execute(text(delete_password_token_sp), {'user_id': all_dangling_accounts_without_stripe_id.user_id})
            db.session.commit()

            delete_all_user_sessions_sp = 'CALL user_schema.delete_all_user_sessions(:user_id)'

            db.session.execute(text(delete_all_user_sessions_sp), {'user_id': all_dangling_accounts_without_stripe_id.user_id})
            db.session.commit()

            left_over_user_id = all_dangling_accounts_without_stripe_id.user_id

            delete_basic_account_create_stripe_customer_id_status_sp = 'CALL payment_schema.delete_basic_account_create_stripe_customer_id_status(:user_id)'

            db.session.execute(text(delete_basic_account_create_stripe_customer_id_status_sp), {'user_id': all_dangling_accounts_without_stripe_id.user_id})
            db.session.commit()

            delete_user_sp = 'CALL user_schema.delete_user(:user_id)'

            db.session.execute(text(delete_user_sp), {'user_id': left_over_user_id})
            db.session.commit()
