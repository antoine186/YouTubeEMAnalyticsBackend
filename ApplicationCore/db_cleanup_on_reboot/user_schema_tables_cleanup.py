from app_start_helper import db
from sqlalchemy import text
from models.youtube_schema.video_analysis_loading_status import VideoAnalysisLoadingStatus

def user_schema_tables_cleanup():
    delete_all_user_session_data_from_user_schema()


def delete_all_user_session_data_from_user_schema():
    """ Delete for
    password_reset
    user_session
    """

    purge_password_reset_sp = 'CALL user_schema.purge_password_reset()'
    db.session.execute(text(purge_password_reset_sp), 
                        {})
    db.session.commit()

    purge_user_session_sp = 'CALL user_schema.purge_user_session()'
    db.session.execute(text(purge_user_session_sp), 
                        {})
    db.session.commit()
