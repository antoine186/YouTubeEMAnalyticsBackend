from app_start_helper import db
from sqlalchemy import text, and_
from models.video_analysis_loading_status import VideoAnalysisLoadingStatus
from db_cleanup_on_reboot.youtube_schema_tables_cleanup import delete_all_loading_video_data_from_youtube_schema
from models.login_log_table import LoginLogTable

def delete_analysis_metadata_from_youtube_schema_for_user(user_id):
    all_loading_videos_for_user = VideoAnalysisLoadingStatus.query.filter(and_(VideoAnalysisLoadingStatus.status == 'true', VideoAnalysisLoadingStatus.user_id == user_id)).all()

    db.session.query(LoginLogTable).filter(LoginLogTable.user_id == user_id).delete()
    db.session.commit()

    for loading_video in all_loading_videos_for_user:
        delete_all_loading_video_data_from_youtube_schema(loading_video.previous_video_analysis_id, user_id)
