from flask import Flask, request, flash, send_from_directory, redirect, current_app, render_template, session, url_for, g
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, connect_db, User, Comment, Post, Like, View
from forms import LoginForm, RegistrationForm, PostImageForm, EditProfileForm, EditPostForm
from config import API_KEY
import requests
import os

# Import the blueprints
from routes.comment import comment_bp
from routes.search import search_bp
from routes.like import like_bp
from routes.dislike import dislike_bp
from routes.post import post_bp
from routes.profile import profile_bp
from routes.author_profile import author_profile_bp
from routes.auth import auth_bp

# Define CURR_USER_KEY if not already defined
CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", 'postgresql:///imgur_clone_db')
connect_db(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = "it's a secret"
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

bcrypt = Bcrypt(app)

# Register the comment blueprint
app.register_blueprint(comment_bp)
app.register_blueprint(search_bp)
app.register_blueprint(like_bp)
app.register_blueprint(dislike_bp)
app.register_blueprint(post_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(author_profile_bp)
app.register_blueprint(auth_bp)

############################################################################################################
# Before each request, add current user to Flask global

@app.before_request
def add_user_to_g():
    """If we're logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

############################################################################################################
# Homepage

@app.route('/')
def index():
    """Homepage with random quote and posts."""
    try:
        quote_data = get_random_quote()
        posts = Post.query.all()

        # Pre-process image URLs
        for post in posts:
            post.img_url = url_for('post.serve_uploaded_image', filename=os.path.basename(post.img_path))

        return render_template('index.html', random_quote=quote_data, posts=posts)
    except requests.RequestException as e:
        current_app.logger.error(f'Error fetching data: {e}')
        quote_data = get_default_quote()
        return render_template('index.html', random_quote=quote_data)

def get_random_quote():
    """Fetch a random quote from an external API."""
    try:
        api_url = 'https://api.api-ninjas.com/v1/quotes'
        headers = {'X-Api-Key': API_KEY}
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()[0]  # Extract first quote from the list
        else:
            current_app.logger.error(f'API request failed with status code {response.status_code}')
            return get_default_quote()
    except requests.RequestException as e:
        current_app.logger.error(f'Error fetching random quote from API: {e}')
        return get_default_quote()

def get_default_quote():
    """Return a default quote."""
    return {
        "quote": "The best way to predict the future is to create it.",
        "author": "Abraham Lincoln",
        "category": "inspirational"
    }