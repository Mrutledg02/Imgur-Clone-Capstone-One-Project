from flask import Blueprint, request, flash, redirect, render_template, session, url_for, g
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from models import db, User
from forms import LoginForm, RegistrationForm
from routes.profile import flash_errors
from routes.helpers import add_user_to_g, do_login, do_logout, CURR_USER_KEY

auth_bp = Blueprint("auth", __name__)

bcrypt = Bcrypt()

@auth_bp.before_request
def before_request():
    add_user_to_g()

############################################################################################################
# Login a user

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Check if username and password are not empty
        if not username or not password:
            return render_template('login.html', form=form, error_message='Username and password are required'), 401
        
        user = User.authenticate(username, password)

        if user:
            do_login(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', form=form, error_message='Invalid username or password'), 401
    else:
        return render_template('login.html', form=form)
    

############################################################################################################
# Register a user

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    form = RegistrationForm(request.form)
 
    if form.validate_on_submit():
            try:
                if form.password.data != form.password_confirm.data:
                    raise ValueError("Passwords do not match")
                
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_password,  # Store hashed password in the database
                )
                db.session.add(user)
                db.session.commit()

                # Automatically log in the user after registration
                do_login(user)

                print("User registered successfully!")
                return redirect(url_for('index'))  # Redirect to index page after registration
            
            except ValueError as error:
                # Handle ValueError (likely due to passwords not matching)
                error_message = str(error)
                print("ValueError:", error_message)
                return render_template('register.html', form=form, error_message=error_message)
            
            except IntegrityError as error:
                # Handle IntegrityError (e.g., duplicate username or email)
                error_message = "Username or email already exists."
                return render_template('register.html', form=form, error_message=error_message), 400

    else:
        # Form validation failed, render form with error messages
        flash_errors(form)
        print("Validation failed:", form.errors)
        return render_template('register.html', form=form)
        
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {getattr(form, field).label.text}: {error}", "error")


############################################################################################################
# Logout a user                                               

@auth_bp.route('/users/logout', methods=['POST'])
def user_logout():
    """Handle logout of user."""
    # Clear the session (logout the user)
    do_logout()

    # Redirect the user to the homepage
    return redirect(url_for('index'))
