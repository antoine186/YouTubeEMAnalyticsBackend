from app_start_helper import db
from sqlalchemy import text
import stripe
from db_cleanup_on_reboot.youtube_schema_tables_cleanup import delete_all_loading_video_data_from_youtube_schema
from Utils.youtube_api_utils.delete_analysis_metadata_from_youtube_schema_for_user import delete_analysis_metadata_from_youtube_schema_for_user
from Utils.logging_utils.delete_logging_data_for_user_helper import delete_logging_data_for_user_helper


def purge_specific_user_by_email(email, delete_remote_stripe_entities):
    """This purging function is unsafe when main program is running
    
    As opposed to stripe_customer_shallow_remote_cleanup(), this function is to
    purge a user from both DB and Stripe where the user was correctly created and
    might have had a successful subscription created.
    """

    if email == '':
        return True

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': email}).fetchall()

    get_internal_stripe_customer_id = 'SELECT payment_schema.get_internal_stripe_customer_id(:user_id)'

    internal_stripe_customer_id = db.session.execute(text(get_internal_stripe_customer_id), {'user_id': user_id[0][0]}).fetchall()

    check_subscription_exists = 'SELECT payment_schema.check_subscription_exists(:internal_stripe_customer_id)'

    subscription_exists = db.session.execute(text(check_subscription_exists), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]}).fetchall()

    if subscription_exists[0][0] == 1:
        if delete_remote_stripe_entities:
            get_stripe_subscription_id = 'SELECT payment_schema.get_stripe_subscription_id(:internal_stripe_customer_id)'

            stripe_subscription_id = db.session.execute(text(get_stripe_subscription_id), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]}).fetchall()

            subscription_to_delete = stripe.Subscription.retrieve(
                stripe_subscription_id[0][0],
            )

            try:
                last_cancelled_invoice = stripe.Invoice.retrieve(
                    subscription_to_delete.latest_invoice,
                )
            except Exception as e:
                print('Apparently there is no invoice to extract from subscription')

            deleted_subscription = stripe.Subscription.delete(
                stripe_subscription_id[0][0],
                prorate=True
            )

        delete_subscription_sp = 'CALL payment_schema.delete_subscription(:internal_stripe_customer_id)'

        db.session.execute(text(delete_subscription_sp), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]})
        db.session.commit()

        if delete_remote_stripe_entities:
            try:
                customer_invoice_list = stripe.InvoiceItem.list(
                    customer=deleted_subscription.customer,
                    pending=True
                )

                amount_to_refund = -customer_invoice_list.data[0].amount

                stripe.InvoiceItem.delete(
                    customer_invoice_list.data[0].id,
                )

                stripe.Refund.create(payment_intent=last_cancelled_invoice.payment_intent, amount=amount_to_refund)
            except Exception as e:
                print('Apparently we cant delete the invoice item and create the refund')

    delete_subscription_sp = 'CALL payment_schema.delete_subscription(:internal_stripe_customer_id)'

    db.session.execute(text(delete_subscription_sp), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]})
    db.session.commit()

    get_stripe_customer_id = 'SELECT payment_schema.get_stripe_customer_id(:internal_stripe_customer_id)'

    stripe_customer_id = db.session.execute(text(get_stripe_customer_id), {'internal_stripe_customer_id': internal_stripe_customer_id[0][0]}).fetchall()

    if delete_remote_stripe_entities:
        if stripe_customer_id[0][0] != None:
            try:
                stripe.Customer.delete(stripe_customer_id[0][0])
            except Exception as e:
                pass
        else:
            stripe_customer_search_result = stripe.Customer.search(
                query="email:'{}'".format(email),
            )

            if len(stripe_customer_search_result._last_response.data['data']) > 0:
                existing_stripe_customer_id = stripe_customer_search_result._last_response.data['data'][0]['id']
                stripe.Customer.delete(existing_stripe_customer_id)

    delete_stripe_subscription_client_secret_sp = 'CALL payment_schema.delete_stripe_subscription_client_secret(:user_id)'

    db.session.execute(text(delete_stripe_subscription_client_secret_sp), {'user_id': user_id[0][0]})
    db.session.commit()

    delete_stripe_customer_sp = 'CALL payment_schema.delete_stripe_customer(:user_id)'

    db.session.execute(text(delete_stripe_customer_sp), {'user_id': user_id[0][0]})
    db.session.commit()

    delete_analysis_metadata_from_youtube_schema_for_user(user_id[0][0])
    delete_logging_data_for_user_helper(user_id[0][0])

    delete_stripe_customer_creation_status_sp = 'CALL payment_schema.delete_stripe_customer_creation_status(:user_id)'

    db.session.execute(text(delete_stripe_customer_creation_status_sp), {'user_id': user_id[0][0]})
    db.session.commit()

    purge_password_reset_sp = 'CALL user_schema.purge_password_reset()'
    db.session.execute(text(purge_password_reset_sp), 
                        {})
    db.session.commit()

    purge_user_session_sp = 'CALL user_schema.purge_user_session()'
    db.session.execute(text(purge_user_session_sp), 
                        {})
    db.session.commit()

    delete_user_sp = 'CALL user_schema.delete_user(:user_id)'

    db.session.execute(text(delete_user_sp), {'user_id': user_id[0][0]})
    db.session.commit()
