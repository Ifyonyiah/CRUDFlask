from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        """Sets the password for the user."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Checks the hashed password against the provided password."""
        return check_password_hash(self.password, password)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30), nullable=False)
    rented_date = db.Column(db.String(10))
    available = db.Column(db.Boolean, default=True)
    available_date = db.Column(db.String(10))
