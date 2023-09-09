from app_start_helper import app, db

with app.app_context():
    class TopNEmotions(db.Model):
        __tablename__ = 'top_n_emotions'
        __table_args__ = {'schema' : 'youtube_schema'}

        top_n_emotions_id = db.Column(db.Integer, primary_key=True)
        previous_video_analysis_id = db.Column(db.Integer)
        top_n_anger = db.Column(db.String)
        top_n_disgust = db.Column(db.String)
        top_n_fear = db.Column(db.String)
        top_n_joy = db.Column(db.String)
        top_n_neutral = db.Column(db.String)
        top_n_sadness = db.Column(db.String)
        top_n_surprise = db.Column(db.String)
