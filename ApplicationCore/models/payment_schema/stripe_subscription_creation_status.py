from app_start_helper import app, db

with app.app_context():
    class StripeSubscriptionCreationStatus(db.Model):
        __tablename__ = 'stripe_subscription_creation_status'
        __table_args__ = {'schema' : 'payment_schema'}

        stripe_subscription_creation_status_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer)
        status = db.Column(db.String(50))
