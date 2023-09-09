from app_start_helper import app, db

with app.app_context():
    class LoginLogTable(db.Model):
        __tablename__ = 'login_log_table'
        __table_args__ = {'schema' : 'logging_schema'}

        login_log_table_id = db.Column(db.Integer, primary_key=True)
        logging_message = db.Column(db.String)
        timestamp = db.Column(db.DateTime)
        user_id = db.Column(db.Integer)
        