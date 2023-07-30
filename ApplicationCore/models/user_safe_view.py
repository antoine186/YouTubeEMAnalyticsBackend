from app_start_helper import app, db

with app.app_context():
    class UserSafeView(db.Model):
        __tablename__ = 'user_safe_view'
        __table_args__ = {'schema' : 'user_schema'}

        user_id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(25))
