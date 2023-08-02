from app_start_helper import app, db

with app.app_context():
    class PreviousVideoAnalysis(db.Model):
        __tablename__ = 'previous_video_analysis'
        __table_args__ = {'schema' : 'youtube_schema'}

        previous_video_analysis_id = db.Column(db.Integer, primary_key=True)
        video_id = db.Column(db.String)
        previous_channel_analysis_id = db.Column(db.Integer)
        previous_video_analysis_json = db.Column(db.String)
        