from flask import Flask, request, flash, send_from_directory, redirect, current_app, render_template, session, url_for, g
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, connect_db, User, Comment, Post, Like
from forms import LoginForm, RegistrationForm, PostImageForm, EditProfileForm, EditPostForm
import requests
import os

# Define CURR_USER_KEY if not already defined
CURR_USER_KEY = "curr_user"

app = Flask(__name__)

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

############################################################################################################
# Before each request, add current user to Flask global

@app.before_request
def add_user_to_g():
    """If we're logged in, add current user to Flask global."""

    # Checking if a user is logged in
    if CURR_USER_KEY in session:
        with app.app_context():
            g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""
    with app.app_context():
        session[CURR_USER_KEY] = user.id
        session.permanent = True  # Setting the session to be permanent


def do_logout():
    """Logout user."""
    with app.app_context():
        if CURR_USER_KEY in session:
            del session[CURR_USER_KEY]


############################################################################################################
# Login a user

# Login a user
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if CURR_USER_KEY in session:
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    form = RegistrationForm(request.form)

    # Print form data to inspect
    print("Form data:", form.data)
    
    if form.validate_on_submit():
        try:
            user = User.create(
                username = form.username.data,
                email = form.email.data,
                password = form.password.data,
                password_confirm = form.password_confirm.data,
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

@app.route('/users/logout', methods=['POST'])
def user_logout():
    """Handle logout of user."""
    # Clear the session (logout the user)
    do_logout()

    # Redirect the user to the homepage
    return redirect(url_for('index'))


############################################################################################################
# Delete a user 

@app.route('/user/delete', methods=['POST'])
def delete_user():
    """Delete a user."""
    if g.user:
        # Delete the user from the database
        db.session.delete(g.user)
        db.session.commit()
        
        # Logout the user after deletion
        do_logout()
        
        flash('Your account has been successfully deleted.', 'success')
        return redirect(url_for('index'))  # Redirect to the homepage or another appropriate page
    else:
        flash('You need to be logged in to delete your account.', 'error')
        return redirect(url_for('login'))  # Redirect to the login page if user is not logged in

############################################################################################################
# User profile

#Upon clicking the profile button, the user should be redirected to the profile page.
@app.route('/profile')
def profile():
    """Display user profile."""
    user = g.user
    if not user:
        return redirect(url_for('login'))

    # Fetch user's upload count
    upload_count = user.uploads

    # Calculate total views for the user's posts
    total_views = user.calculate_total_views()

    return render_template('profile.html', user=user, upload_count=upload_count, total_views=total_views)

@app.route('/user_posts/<username>')
def user_posts(username):
    """Display posts of a specific user."""
    # Fetch the user based on the username parameter
    user = User.query.filter_by(username=username).first()
    if not user:
        # Handle case where user does not exist
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    # Fetch user's posts
    user_posts = Post.query.filter_by(fk_userid=user.id).all()        
    
    # Pre-process image URLs
    for post in user_posts:
        post.img_url = url_for('serve_uploaded_image', filename=os.path.basename(post.img_path))
    
    # Calculate total views for the user's posts
    total_views = user.calculate_total_views()
    
    return render_template('user_posts.html', user=user, user_posts=user_posts, total_views=total_views)

# Route to display posts liked by the user
@app.route('/user_likes/<username>')
def user_likes(username):
    """Display posts liked by the user."""
    # Ensure the user is logged in
    if not g.user:
        flash('Please log in to view your liked posts.', 'error')
        return redirect(url_for('login'))

    # Fetch the user based on the username parameter
    user = User.query.filter_by(username=username).first_or_404()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('index'))

    # Fetch the liked posts of the authenticated user
    liked_posts = (
        Post.query
        .join(Like, Post.id == Like.post_id)
        .filter(Like.user_id == user.id)
        .filter(Like.is_like == True)
        .all()
    )

    # Pre-process image URLs for liked posts
    for post in liked_posts:
        post.img_url = url_for('serve_uploaded_image', filename=os.path.basename(post.img_path))

    # Calculate total views for the user's posts
    total_views = user.calculate_total_views()

    return render_template('user_likes.html', user=user, liked_posts=liked_posts, total_views=total_views)

# Route to display comments of the currently logged-in user
@app.route('/user_comments/<username>')
def user_comments(username):
    """Display comments made by the user."""

    user = User.query.filter_by(username=username).first()

    if not user:
        return redirect(url_for('login'))

    # Fetch user's comments along with associated post information
    user_comments = (
        Comment.query
        .join(Post, Comment.fk_postid == Post.id)  # Join Comment with Post
        .filter(Comment.fk_userid == user.id)  # Filter comments by user ID
        .order_by(Comment.created.desc())
        .all()
    )

    # Pre-process image URLs for each comment's associated post
    for comment in user_comments:
        comment.post.img_url = url_for('serve_uploaded_image', filename=os.path.basename(comment.post.img_path))

    # Calculate total views for the user's posts
    total_views = user.calculate_total_views()

    return render_template('user_comments.html', user=user, user_comments=user_comments, total_views=total_views)

@app.route('/user_about/<username>')
def user_about(username):
    """Display the about page of a specific user."""
    # Retrieve user information based on username (e.g., from the database)
    user = User.query.filter_by(username=username).first()
    if user:
        # Calculate total views for the user's posts
        total_views = user.calculate_total_views()
        return render_template('user_about.html', user=user, total_views=total_views)
    else:
        # Handle case where user is not found
        return render_template('user_not_found.html')
    
############################################################################################################
# Author profile

#Upon clicking the author's name for a post, the user should be redirected to the author's profile page.
@app.route('/author/<username>')
def author_profile(username):
    """Display author profile."""
    author = User.query.filter_by(username=username).first()
    if not author:
        # Handle case where author does not exist
        flash('Author not found', 'error')
        return redirect(url_for('index'))  # Redirect to homepage or appropriate page

    # Fetch author's posts
    author_posts = Post.find_user_posts(username)

    # Pre-process image URLs
    for post in author_posts:
        post.img_url = url_for('serve_uploaded_image', filename=os.path.basename(post.img_path))

    return render_template('author_profile.html', author=author, author_posts=author_posts)

# Route to display posts of a specific author
@app.route('/author_posts/<username>')
def author_posts(username):
    """Display posts of a specific author."""
    author = User.query.filter_by(username=username).first()
    if not author:
        flash('Author not found', 'error')
        return redirect(url_for('index'))

    # Fetch author's posts
    author_posts = Post.query.filter_by(fk_userid=author.id).all()

    # Pre-process image URLs for author's posts
    for post in author_posts:
        post.img_url = url_for('serve_uploaded_image', filename=os.path.basename(post.img_path))

    return render_template('author_posts.html', author=author, author_posts=author_posts)

# Route to display posts liked by a specific author
@app.route('/author_likes/<username>')
def author_likes(username):
    """Display posts liked by a specific author."""
    # Fetch the user based on the username parameter
    author = User.query.filter_by(username=username).first()
    if not author:
        flash('Author not found', 'error')
        return redirect(url_for('index'))

    # Fetch the liked posts of the author
    liked_posts = (
        Post.query
        .join(Like, Post.id == Like.post_id)
        .join(User, Like.user_id == User.id)
        .filter(User.username == username)
        .all()
    )

    # Pre-process image URLs for liked posts
    for post in liked_posts:
        post.img_url = url_for('serve_uploaded_image', filename=os.path.basename(post.img_path))

    return render_template('author_likes.html', author=author, liked_posts=liked_posts)

# Route to display comments made by a specific author
@app.route('/author_comments/<username>')
def author_comments(username):
    """Display comments made by a specific author."""
    author = User.query.filter_by(username=username).first()
    if not author:
        # Handle case where author does not exist
        flash('Author not found', 'error')
        return redirect(url_for('index'))  # Redirect to homepage or appropriate page
    
    # Fetch author's comments
    author_comments = (
        Comment.query
        .join(User, Comment.fk_userid == User.id)  # Join Comment with User
        .filter(User.username == username)  # Filter comments by username
        .order_by(Comment.created.desc())
        .all()
    )

    # Pre-process image URLs for each comment's associated post
    for comment in author_comments:
        comment.post.img_url = url_for('serve_uploaded_image', filename=os.path.basename(comment.post.img_path))

    return render_template('author_comments.html', author=author, author_comments=author_comments)

# Route to display the about page of a specific author
@app.route('/author_about/<username>')
def author_about(username):
    """Display the about page of a specific author."""
    author = User.query.filter_by(username=username).first()
    if not author:
        flash('Author not found', 'error')
        return redirect(url_for('index'))

    return render_template('author_about.html', author=author)

############################################################################################################
# Edits

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    """Edit user profile."""
    form = EditProfileForm(request.form)

    if form.validate_on_submit():
        user = g.user
        
        if user:
            # Update user's information based on form data
            new_username = form.username.data
            new_email = form.email.data
            new_password = form.password.data
            new_about = form.about.data

            # Update username if provided
            if new_username:
                user.username = new_username

            # Update email if provided
            if new_email:
                user.email = new_email

            # Update password if provided
            if new_password:
                hashed_pwd = bcrypt.generate_password_hash(new_password).decode('UTF-8')
                user.password = hashed_pwd

            # Update about if provided
            if new_about:
                user.about = new_about

            # Commit changes to the database
            db.session.commit()

            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile'))
        else:
            flash('User not found', 'error')
            return redirect(url_for('login'))
    else:
        flash_errors(form)
        return render_template('edit_profile.html', form=form)

def flash_errors(form):
    """Flash form errors."""
    for field, errors in form.errors.items():
        # Skip flashing CSRF token errors
        if field != 'csrf_token':
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "error")

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    """Edit a post."""
    post = Post.query.get_or_404(post_id)
    form = EditPostForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        # Handle image upload if a new image is provided
        if form.upload_image.data:
            # Handle image upload logic here
            pass  # Replace this with your logic to upload and save the image
        db.session.commit()
        flash('Post updated successfully', 'success')
        return redirect(url_for('show_image', post_id=post.id))
    return render_template('edit_post.html', form=form)

############################################################################################################
# Homepage

@app.route('/')
def index():
    """Homepage with random quote and posts."""
    try:
        api_url = 'https://api.api-ninjas.com/v1/quotes'
        headers = {'X-Api-Key': 'WYRNpzUj6vYvDkA5u5RiYQ==CfYvstSN48hBCZfn'}
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            quote_data = response.json()[0]  # Extract first quote from the list
            
            # Fetch all posts
            posts = Post.query.all()
            
            # Pre-process image URLs
            for post in posts:
                post.img_url = url_for('serve_uploaded_image', filename=os.path.basename(post.img_path))

            return render_template('index.html', random_quote=quote_data, posts=posts)
        else:
            current_app.logger.error(f'API request failed with status code {response.status_code}')
            return render_template('index.html', random_quote=get_default_quote())
    except requests.RequestException as e:
        current_app.logger.error(f'Error fetching random quote from API: {e}')
        return render_template('index.html', random_quote=get_default_quote())

def get_default_quote():
    """Return a default quote if the API request fails."""
    return {
        "quote": "The best way to predict the future is to create it.",
        "author": "Abraham Lincoln",
        "category": "inspirational"
    }

############################################################################################################
# Post upload and Post

# Route to render HTML template for uploading an image
@app.route('/postImage', methods=['GET', 'POST'])
def upload_image():
    """Handle image upload."""
    form = PostImageForm()

    if form.validate_on_submit():
            title = form.title.data
            description = form.description.data
            file_uploaded = form.uploadImage.data
            user_id = g.user.id if g.user else None

            if not title or not description:
                flash('Please include a title and description.', 'error')
            elif not user_id:
                flash('User is not authenticated.', 'error')
            elif not file_uploaded:
                flash('No image file uploaded.', 'error')
            else:
                filename = secure_filename(file_uploaded.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_uploaded.save(file_path)
                
                post = Post(title=title, description=description, img_path=file_path, fk_userid=user_id)
                db.session.add(post)
                db.session.commit()

                # Increment the user's upload count
                increment_user_uploads(user_id)
                
                flash('Post uploaded successfully.', 'success')
                return redirect(url_for('show_image', post_id=post.id))
        
    return render_template('postImage.html', form=form)

# Function to increment the user's upload count
def increment_user_uploads(user_id):
    """Increment the user's upload count."""
    with app.app_context():
        user = User.query.get(user_id)
        if user:
            user.uploads += 1
            db.session.commit()   

# Route to serve uploaded images
@app.route('/uploads/<filename>')
def serve_uploaded_image(filename):
    """Serve uploaded images."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to render HTML template for displaying a post once uploaded
@app.route('/image/<int:post_id>')
def show_image(post_id):
    """Display a specific post."""
    post = Post.query.get_or_404(post_id)
    img_filename = os.path.basename(post.img_path)

    if img_filename:
        img_url = url_for('serve_uploaded_image', filename=img_filename)
        comments = Comment.get_post_comments(post_id)  # Fetch comments for the post

        # Check if user is logged in
        if CURR_USER_KEY not in session:
            flash('Please login to view post.', 'error')
            return redirect(url_for('login'))

        # Check if the current user has already liked or disliked the post
        user_id = g.user.id if g.user else None
        already_liked = False
        already_disliked = False
        if user_id:
            existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
            if existing_like:
                if existing_like.is_like:
                    already_liked = True
                else:
                    already_disliked = True

        # Check if the current user is the author of the post
        is_author = False
        if g.user and g.user.id == post.fk_userid:
            is_author = True

        # Increment views for the current post if the user viewing it is not the author
        if not is_author:
            Post.increment_views(post_id)

        return render_template('image.html', post=post, img_url=img_url, comments=comments,
                               already_liked=already_liked, already_disliked=already_disliked,
                               is_author=is_author)
    else:       
        flash('Error fetching image.', 'error')
        return redirect(url_for('index'))
    

# Route to handle deleting a post, and decrementing the user's upload count
def decrement_user_uploads(user_id):
    """Decrement the user's upload count."""
    with app.app_context():
        user = User.query.get(user_id)
        if user and user.uploads > 0:
            user.uploads -= 1
            db.session.commit()  

# Route to delete a post
@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Delete a post."""
    post = Post.query.get_or_404(post_id)

    # Check if the current user is the author of the post
    if post.user != g.user:
        flash("You are not authorized to delete this post", "error")
        return redirect(url_for('index'))

    # Delete associated comments
    Comment.query.filter_by(fk_postid=post_id).delete()

    # Delete associated likes
    Like.query.filter_by(post_id=post_id).delete()

    # Delete the post
    db.session.delete(post)
    db.session.commit()

    # Decrement the user's upload count
    decrement_user_uploads(g.user.id)

    flash("Post deleted successfully", "success")
    return redirect(url_for('index'))


############################################################################################################
# Comments 

# Route to add a comment to a specific post
@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment_to_specific_post(post_id):
    """Add a comment to a specific post."""
    data = request.form  # Assuming form data is sent via POST request
    user_id = g.user.id if g.user else None
    text = data.get('text')
    if not user_id:
            flash('User not logged in', 'error')
            return redirect(url_for('show_image', post_id=post_id))  # Redirect back to the post page

    success = Comment.add_post_comment(post_id, user_id, text)
    if success:
        flash('Comment added successfully', 'success')
        return redirect(url_for('show_image', post_id=post_id))  # Redirect back to the post page
    else:
        flash('Failed to add comment', 'error')
        return redirect(url_for('show_image', post_id=post_id))  # Redirect back to the post page

############################################################################################################
# Search

# Route to handle search queries
@app.route('/search')
def search():
    """Handle search queries."""
    # Get the search query from the request
    query = request.args.get('query')

    # Query your database based on the search query using the find_many method
    search_results = Post.find_many(query)

    # Pre-process image URLs
    for post in search_results:
        post.img_url = url_for('serve_uploaded_image', filename=os.path.basename(post.img_path))

    # Render the search results in the search.html template
    return render_template('search.html', query=query, posts=search_results)


############################################################################################################
# Liking

# Route to handle liking a post
@app.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like a post."""
    post = Post.query.get_or_404(post_id)
    user_id = g.user.id if g.user else None
    
    if not user_id:
        flash('User not logged in', 'error')
        return redirect(url_for('login', post_id=post_id))
    
    existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    if existing_like:
        if existing_like.is_like:
            post.likes_count -= 1
        else:
            post.dislikes_count -= 1
        db.session.delete(existing_like)
    else:
        like = Like(post_id=post_id, user_id=user_id, is_like=True)
        db.session.add(like)
        post.likes_count += 1

    db.session.commit()  # Move the commit outside the if-else block

    # Print request referrer for debugging
    print("Request Referrer:", request.referrer)
    
    # Determine the redirect URL based on the request referrer
    if request.referrer and 'show_image' in request.referrer:
        return redirect(url_for('show_image', post_id=post_id))
    elif request.referrer and 'index' in request.referrer:
        return redirect(url_for('index'))
    else:
        # Redirect back to the referrer URL if not show_image or index
        return redirect(request.referrer or url_for('index'))

# Route to handle disliking a post
@app.route('/post/<int:post_id>/dislike', methods=['POST'])
def dislike_post(post_id):
    """Dislike a post."""
    post = Post.query.get_or_404(post_id)
    user_id = g.user.id if g.user else None
    
    if not user_id:
        flash('User not logged in', 'error')
        return redirect(url_for('login', post_id=post_id))
    
    existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    
    if existing_like:
        if not existing_like.is_like:
            post.dislikes_count -= 1
        else:
            post.likes_count -= 1
        db.session.delete(existing_like)
    else:
        like = Like(post_id=post_id, user_id=user_id, is_like=False)
        db.session.add(like)
        post.dislikes_count += 1

    db.session.commit()  # Move the commit outside the if-else block

    # Print request referrer for debugging
    print("Request Referrer:", request.referrer)
    
    # Determine the redirect URL based on the request referrer
    if request.referrer and 'show_image' in request.referrer:
        return redirect(url_for('show_image', post_id=post_id))
    elif request.referrer and 'index' in request.referrer:
        return redirect(url_for('index'))
    else:
        # Redirect back to the referrer URL if not show_image or index
        return redirect(request.referrer or url_for('index'))