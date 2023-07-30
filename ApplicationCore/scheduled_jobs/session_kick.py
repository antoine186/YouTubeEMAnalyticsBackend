from app_start_helper import scheduler
from app_start_helper import db
from sqlalchemy import text
from app_start_helper import app

# This for prod
number_of_seconds = 3600

def session_kick():
    scheduler.add_job(func=session_kick_job, trigger="interval", seconds=number_of_seconds)

def session_kick_job():
    with app.app_context():
        auto_delete_user_session_sp = 'CALL user_schema.auto_delete_user_session()'

        db.session.execute(text(auto_delete_user_session_sp))

        db.session.commit()
