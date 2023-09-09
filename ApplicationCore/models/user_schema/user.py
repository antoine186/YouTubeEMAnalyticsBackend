from app_start_helper import app, db

with app.app_context():
    class User(db.Model):
        __tablename__ = 'user'
        __table_args__ = {'schema' : 'user_schema'}

        user_id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(25))
        password = db.Column(db.String(25))
        first_name = db.Column(db.String(25))
        last_name = db.Column(db.String(25))
        primary_email = db.Column(db.String(25))
        date_of_birth = db.Column(db.DateTime)
        telephone_number = db.Column(db.String(25))
        telephone_area_code = db.Column(db.String(25))
