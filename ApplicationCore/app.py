import sys
sys.path.append('ApplicationCore')
sys.path.append('ApplicationCore/routes')
sys.path.append('ApplicationCore/scheduled_jobs')
from scheduled_jobs.session_kick import session_kick
from scheduled_jobs.error_logs_purge import error_logs_purge
from scheduled_jobs.apscheduler_start_cleanup import apscheduler_start_cleanup
from db_cleanup_on_reboot.youtube_schema_tables_cleanup import youtube_schema_tables_cleanup
from db_cleanup_on_reboot.user_schema_tables_cleanup import user_schema_tables_cleanup
from purging_scripts_debug_only.purge_specific_user_by_email import purge_specific_user_by_email
from stripe_cleanup_on_reboot.stripe_customer_shallow_remote_cleanup import stripe_customer_shallow_remote_cleanup
from subscription_cleanup_on_reboot.subscription_halted_creation_cleanup_on_reboot import subscription_halted_creation_cleanup_on_reboot
from account_cleanup_on_reboot.dangling_account_without_stripe_account_cleanup import dangling_account_without_stripe_account_cleanup

from app_start_helper import app, db, debug_switched_on, debug_purging_on, remote_stripe_entities_purging, purge_dangling_accounts_without_stripe_id, \
    remote_purge_halted_subscriptions

from main_pages.main_page_blueprint import main_page_blueprint
from authentication.authentication_blueprint import authentication_blueprint
from authentication.session_authentication_blueprint import session_authentication_blueprint
from account_data.basic_account_creation_blueprint import basic_account_creation_blueprint
from payment.stripe_customer_creation_blueprint import stripe_customer_creation_blueprint
from payment.subscription_creation_blueprint import subscription_creation_blueprint
from payment.get_subscription_status_blueprint import get_subscription_status_blueprint
from payment.get_subscription_id_blueprint import get_subscription_id_blueprint
from payment.store_new_subscription_blueprint import store_new_subscription_blueprint
from payment.update_subscription_status_blueprint import update_subscription_status_blueprint
from account_data.delete_account_blueprint import delete_account_blueprint
from payment.retrieve_subscription_details_blueprint import retrieve_subscription_details_blueprint
from account_data.retrieve_account_data_blueprint import retrieve_account_data_blueprint
from payment.setupintent_creation_blueprint import setupintent_creation_blueprint
from payment.get_stripe_customer_id_blueprint import get_stripe_customer_id_blueprint
from payment.delete_subscription_blueprint import delete_subscription_blueprint
from authentication.forgot_password_blueprint import forgot_password_blueprint
from authentication.password_reset_blueprint import password_reset_blueprint
from search.get_previous_search_result_blueprint import get_previous_search_result_blueprint
from payment.create_checkout_blueprint import create_checkout_blueprint
from youtube_channel.youtube_analyse_blueprint import youtube_analyse_blueprint
from youtube_channel.youtube_retrieve_channel_results_blueprint import youtube_retrieve_channel_results_blueprint
from youtube_channel.comments_llm_questioning_blueprint import comments_llm_questioning_blueprint
from youtube_channel.comments_llm_emo_elaboration_blueprint import comments_llm_emo_elaboration_blueprint
from youtube_channel.youtube_video_adhoc_analyse_blueprint import youtube_video_adhoc_analyse_blueprint
from youtube_channel.youtube_retrieve_video_adhoc_results_blueprint import youtube_retrieve_video_adhoc_results_blueprint
from authentication.remove_session_blueprint import remove_session_blueprint
from server.check_if_server_up_blueprint import check_if_server_up_blueprint
from configuration_data.session_configuration_data_blueprint import session_configuration_data_blueprint

app.register_blueprint(main_page_blueprint)
app.register_blueprint(authentication_blueprint)
app.register_blueprint(session_authentication_blueprint)
app.register_blueprint(basic_account_creation_blueprint)
app.register_blueprint(stripe_customer_creation_blueprint)
app.register_blueprint(subscription_creation_blueprint)
app.register_blueprint(get_subscription_status_blueprint)
app.register_blueprint(get_subscription_id_blueprint)
app.register_blueprint(store_new_subscription_blueprint)
app.register_blueprint(update_subscription_status_blueprint)
app.register_blueprint(delete_account_blueprint)
app.register_blueprint(retrieve_subscription_details_blueprint)
app.register_blueprint(retrieve_account_data_blueprint)
app.register_blueprint(get_stripe_customer_id_blueprint)
app.register_blueprint(delete_subscription_blueprint)
app.register_blueprint(forgot_password_blueprint)
app.register_blueprint(password_reset_blueprint)
app.register_blueprint(get_previous_search_result_blueprint)
app.register_blueprint(create_checkout_blueprint)
app.register_blueprint(youtube_analyse_blueprint)
app.register_blueprint(youtube_retrieve_channel_results_blueprint)
app.register_blueprint(comments_llm_questioning_blueprint)
app.register_blueprint(comments_llm_emo_elaboration_blueprint)
app.register_blueprint(youtube_video_adhoc_analyse_blueprint)
app.register_blueprint(youtube_retrieve_video_adhoc_results_blueprint)
app.register_blueprint(remove_session_blueprint)
app.register_blueprint(check_if_server_up_blueprint)
app.register_blueprint(session_configuration_data_blueprint)

with app.app_context():
    db.init_app(app)

    if remote_purge_halted_subscriptions:
        subscription_halted_creation_cleanup_on_reboot()

    if remote_stripe_entities_purging and not purge_dangling_accounts_without_stripe_id:
        # DB and remote Stripe cleanup on boot up
        stripe_customer_shallow_remote_cleanup()

    if purge_dangling_accounts_without_stripe_id:
        dangling_account_without_stripe_account_cleanup()

    if debug_switched_on:
        if debug_purging_on:
            # Purging on !!! DEBUG ONLY !!!
            # Set email to '' if there is nothing to purge

            #purge_specific_user_by_email('antoine186@hotmail.com', remote_stripe_entities_purging)
            purge_specific_user_by_email('', remote_stripe_entities_purging)

    # DB cleanups on boot up
    youtube_schema_tables_cleanup()
    user_schema_tables_cleanup()

    session_kick()
    #tagging_update()
    error_logs_purge()
    apscheduler_start_cleanup()

if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True)
