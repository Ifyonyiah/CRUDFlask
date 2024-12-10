from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, RentalForm  # Ensure these are defined

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # Placeholder for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Rental model
class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30), nullable=False)
    rented_date = db.Column(db.String(10))
    available = db.Column(db.Boolean, default=True)
    available_date = db.Column(db.String(10))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all tables defined in your models when the app starts
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
@login_required
def index():
    rentals = Rental.query.all()
    return render_template('index.html', rentals=rentals)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('new_rental'))  # Redirecting to the new_rental route
        flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/new_rental', methods=['GET', 'POST'])  # New rental route
@login_required
def new_rental():
    form = RentalForm()
    if form.validate_on_submit():
        rental = Rental(
            make=form.make.data,
            model=form.model.data,
            year=form.year.data,
            color=form.color.data,
            available=form.available.data
        )
        db.session.add(rental)
        db.session.commit()
        flash('Rental created successfully!', 'success')
        return redirect(url_for('index'))  # Redirect to index after creation
    return render_template('new_rental.html', form=form)

@app.route('/edit_rental/<int:rental_id>', methods=['GET', 'POST'])  # Add this route
@login_required
def edit_rental(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    form = RentalForm(obj=rental)  # Prepopulate the form with existing rental data
    if form.validate_on_submit():
        rental.make = form.make.data
        rental.model = form.model.data
        rental.year = form.year.data
        rental.color = form.color.data
        rental.available = form.available.data
        db.session.commit()
        flash('Rental updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_rental.html', form=form, rental=rental)

@app.route('/delete_rental/<int:rental_id>', methods=['POST'])  # Add this route
@login_required
def delete_rental(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    db.session.delete(rental)
    db.session.commit()
    flash('Rental deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
