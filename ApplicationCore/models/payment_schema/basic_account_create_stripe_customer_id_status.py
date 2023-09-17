from app_start_helper import app, db

with app.app_context():
    class BasicAccountCreateStripeCustomerIdStatus(db.Model):
        __tablename__ = 'basic_account_create_stripe_customer_id_status'
        __table_args__ = {'schema' : 'payment_schema'}

        basic_account_create_stripe_customer_id_status_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer)
        status = db.Column(db.String(50))