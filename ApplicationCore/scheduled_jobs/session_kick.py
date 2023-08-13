from app_start_helper import scheduler, db, app, debug_switched_on, number_of_seconds_prod, number_of_seconds_debug
from sqlalchemy import text

if debug_switched_on:
    number_of_seconds = number_of_seconds_debug
else:
    number_of_seconds = number_of_seconds_prod

def session_kick():
    scheduler.add_job(func=session_kick_job, trigger="interval", seconds=number_of_seconds)

def session_kick_job():
    with app.app_context():
        if debug_switched_on:
            auto_delete_user_session_sp = 'CALL user_schema.auto_delete_user_session_for_testing()'
        else:
            auto_delete_user_session_sp = 'CALL user_schema.auto_delete_user_session()'

        db.session.execute(text(auto_delete_user_session_sp))

        db.session.commit()
