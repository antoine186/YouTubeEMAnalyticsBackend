from app_start_helper import db
from sqlalchemy import text

def full_cleanup_account_data_backend_only(user_id, wipe_session_data, wipe_stripe_data, wipe_subscription_data):
    """
    DONT USE, Currently not part of the testing suite
    """
    # Delete entire account on backend
    # Delete from payment schema
    if wipe_stripe_data:
        delete_stripe_customer_creation_status_sp = 'CALL payment_schema.delete_stripe_customer_creation_status(:user_id)'

        db.session.execute(text(delete_stripe_customer_creation_status_sp), {'user_id': user_id})
        db.session.commit()

    if wipe_subscription_data:
        delete_stripe_subscription_creation_status_sp = 'CALL payment_schema.delete_stripe_subscription_creation_status(:user_id)'

        db.session.execute(text(delete_stripe_subscription_creation_status_sp), {'user_id': user_id})
        db.session.commit()

        get_internal_stripe_customer_id = 'SELECT payment_schema.get_internal_stripe_customer_id(:user_id)'
        internal_stripe_customer_id = db.session.execute(text(get_internal_stripe_customer_id), {'user_id': user_id}).fetchall()

        # Can simply delete subscription in backend because deleting the stripe customer will delete the corresponding subscriptions
        if internal_stripe_customer_id[0][0] != None:
            delete_subscription_sp = 'CALL payment_schema.delete_subscription(:internal_stripe_customer_id)'

            db.session.execute(text(delete_subscription_sp), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]})
            db.session.commit()

    if wipe_stripe_data:
        delete_stripe_customer_sp = 'CALL payment_schema.delete_stripe_customer(:user_id)'

        db.session.execute(text(delete_stripe_customer_sp), {'user_id': user_id})
        db.session.commit()

    # Delete from logging schema
    if wipe_session_data:
        delete_all_login_log_entries_for_users_sp = 'CALL logging_schema.delete_all_login_log_entries_for_users(:user_id)'

        db.session.execute(text(delete_all_login_log_entries_for_users_sp), {'user_id': user_id})
        db.session.commit()

    # Delete from user schema
    delete_address_sp = 'CALL user_schema.delete_address(:user_id)'

    db.session.execute(text(delete_address_sp), {'user_id': user_id})
    db.session.commit()

    if wipe_session_data:
        delete_password_token_sp = 'CALL user_schema.delete_password_token(:user_id)'

        db.session.execute(text(delete_password_token_sp), {'user_id': user_id})
        db.session.commit()

        delete_all_user_sessions_sp = 'CALL user_schema.delete_all_user_sessions(:user_id)'

        db.session.execute(text(delete_all_user_sessions_sp), {'user_id': user_id})
        db.session.commit()

    delete_basic_account_create_stripe_customer_id_status_sp = 'CALL payment_schema.delete_basic_account_create_stripe_customer_id_status(:user_id)'

    db.session.execute(text(delete_basic_account_create_stripe_customer_id_status_sp), {'user_id': user_id})
    db.session.commit()

    delete_user_sp = 'CALL user_schema.delete_user(:user_id)'

    db.session.execute(text(delete_user_sp), {'user_id': user_id})
    db.session.commit()

