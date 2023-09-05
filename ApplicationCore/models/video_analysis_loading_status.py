from app_start_helper import app, db

with app.app_context():
    class VideoAnalysisLoadingStatus(db.Model):
        __tablename__ = 'video_analysis_loading_status'
        __table_args__ = {'schema' : 'youtube_schema'}

        video_analysis_loading_status_id = db.Column(db.Integer, primary_key=True)
        previous_video_analysis_id = db.Column(db.Integer)
        status = db.Column(db.String)
        user_id = db.Column(db.Integer)
