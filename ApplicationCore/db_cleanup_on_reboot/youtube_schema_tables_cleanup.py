from app_start_helper import db
from sqlalchemy import text
from models.youtube_schema.video_analysis_loading_status import VideoAnalysisLoadingStatus

def youtube_schema_tables_cleanup():
    all_loading_videos = VideoAnalysisLoadingStatus.query.filter(VideoAnalysisLoadingStatus.status == 'true').all()

    for loading_video in all_loading_videos:
        delete_all_loading_video_data_from_youtube_schema(loading_video.previous_video_analysis_id, loading_video.user_id)


def delete_all_loading_video_data_from_youtube_schema(previous_video_analysis_id, user_id):
    """ Delete for
    comment_emo_breakdown
    previous_video_analysis_latest_date
    top_n_emotions
    user_searched_video
    video_analysis_loading_status
    video_approximated_description
    video_not_enough_comments
    who_are_viewers_approximated
    previous_video_analysis
    """

    delete_emo_breakdown_comments_sp = 'CALL youtube_schema.delete_emo_breakdown_comments(:previous_video_analysis_id)'
    db.session.execute(text(delete_emo_breakdown_comments_sp), 
                        {'previous_video_analysis_id': previous_video_analysis_id})
    db.session.commit()

    delete_latest_video_analysis_date_sp = 'CALL youtube_schema.delete_latest_video_analysis_date(:previous_video_analysis_id)'
    db.session.execute(text(delete_latest_video_analysis_date_sp), 
                        {'previous_video_analysis_id': previous_video_analysis_id})
    db.session.commit()

    delete_top_n_emotions_sp = 'CALL youtube_schema.delete_top_n_emotions(:previous_video_analysis_id)'
    db.session.execute(text(delete_top_n_emotions_sp), 
                        {'previous_video_analysis_id': previous_video_analysis_id})
    db.session.commit()

    delete_top_n_emotions_sp = 'CALL youtube_schema.delete_top_n_emotions(:previous_video_analysis_id)'
    db.session.execute(text(delete_top_n_emotions_sp), 
                        {'previous_video_analysis_id': previous_video_analysis_id})
    db.session.commit()

    delete_user_searched_video_sp = 'CALL youtube_schema.delete_user_searched_video(:user_id)'
    db.session.execute(text(delete_user_searched_video_sp), 
                        {'user_id': user_id})
    db.session.commit()

    delete_video_analysis_status_sp = 'CALL youtube_schema.delete_video_analysis_status(:previous_video_analysis_id)'
    db.session.execute(text(delete_video_analysis_status_sp), 
                        {'previous_video_analysis_id': previous_video_analysis_id})
    db.session.commit()

    delete_video_approximated_description_sp = 'CALL youtube_schema.delete_video_approximated_description(:previous_video_analysis_id)'
    db.session.execute(text(delete_video_approximated_description_sp), 
                        {'previous_video_analysis_id': previous_video_analysis_id})
    db.session.commit()

    delete_video_not_enough_comments_status_sp = 'CALL youtube_schema.delete_video_not_enough_comments_status(:previous_video_analysis_id)'
    db.session.execute(text(delete_video_not_enough_comments_status_sp), 
                        {'previous_video_analysis_id': previous_video_analysis_id})
    db.session.commit()

    delete_who_are_viewers_approximated_sp = 'CALL youtube_schema.delete_who_are_viewers_approximated(:previous_video_analysis_id)'
    db.session.execute(text(delete_who_are_viewers_approximated_sp), 
                        {'previous_video_analysis_id': previous_video_analysis_id})
    db.session.commit()

    delete_video_analysis_sp = 'CALL youtube_schema.delete_video_analysis(:previous_video_analysis_id)'
    db.session.execute(text(delete_video_analysis_sp), 
                        {'previous_video_analysis_id': previous_video_analysis_id})
    db.session.commit()
