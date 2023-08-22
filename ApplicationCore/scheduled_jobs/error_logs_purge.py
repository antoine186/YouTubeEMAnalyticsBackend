import sys
sys.path.append('ApplicationCore')

from app_start_helper import scheduler, db, app, debug_switched_on, number_of_seconds_prod, number_of_seconds_debug
from sqlalchemy import text

if debug_switched_on:
    number_of_seconds = number_of_seconds_debug
else:
    number_of_seconds = number_of_seconds_prod

def error_logs_purge():
    scheduler.add_job(func=error_logs_purge_job, trigger="interval", seconds=number_of_seconds)

def error_logs_purge_job():
    with app.app_context():
        auto_delete_login_error_entry_sp = 'CALL logging_schema.auto_delete_login_error_entry()'

        db.session.execute(text(auto_delete_login_error_entry_sp))

        db.session.commit()
