from app_start_helper import app, db

with app.app_context():
    class TaggingInput(db.Model):
        __tablename__ = 'tagging_input'
        __table_args__ = {'schema' : 'search_schema'}

        tagging_input_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer)
        tagging_input_list = db.Column(db.String(500))
