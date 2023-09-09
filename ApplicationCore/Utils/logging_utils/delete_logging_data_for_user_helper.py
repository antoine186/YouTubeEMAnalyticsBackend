from app_start_helper import db
from sqlalchemy import text

def delete_logging_data_for_user_helper(user_id):
    delete_all_login_log_entries_for_users_sp = 'CALL logging_schema.delete_all_login_log_entries_for_users(:user_id)'

    db.session.execute(text(delete_all_login_log_entries_for_users_sp), {'user_id': user_id})
    db.session.commit()
