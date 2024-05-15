from flask import Flask, Blueprint, request, flash, send_from_directory, redirect, current_app, render_template, session, url_for, g
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os

from models import db, User, Comment, Post, Like, View
from forms import EditProfileForm
from routes.helpers import add_user_to_g, do_login, do_logout, CURR_USER_KEY

profile_bp = Blueprint('profile', __name__)

app = Flask(__name__)

bcrypt = Bcrypt(app)

@profile_bp.before_request
def before_request():
    add_user_to_g()

############################################################################################################
# User profile

#Upon clicking the profile button, the user should be redirected to the profile page.
@profile_bp.route('/profile')
def profile():
    """Display user profile."""
    user = g.user
    if not user:
        return redirect(url_for('login'))

    # Fetch user's upload count
    upload_count = user.uploads

    # Calculate total views for the user's posts
    total_views = user.calculate_total_views()

    # Pass the username to the template
    username = user.username

    return render_template('profile.html', user=user, upload_count=upload_count, total_views=total_views, username=username)

@profile_bp.route('/user_posts/<username>')
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
        post.img_url = url_for('post.serve_uploaded_image', filename=os.path.basename(post.img_path))
    
    # Calculate total views for the user's posts
    total_views = user.calculate_total_views()

    # Pass the username to the template
    username = user.username
    
    return render_template('user_posts.html', user=user, user_posts=user_posts, total_views=total_views, username=username)

# Route to display posts liked by the user
@profile_bp.route('/user_likes/<username>')
def user_likes(username):
    """Display posts liked by the user."""
    # Ensure the user is logged in
    if not g.user:
        flash('Please log in to view your liked posts.', 'error')
        return redirect(url_for('auth.login'))

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
        post.img_url = url_for('post.serve_uploaded_image', filename=os.path.basename(post.img_path))

    # Calculate total views for the user's posts
    total_views = user.calculate_total_views()

    # Pass the username to the template
    username = user.username

    return render_template('user_likes.html', user=user, liked_posts=liked_posts, total_views=total_views, username=username)

# Route to display comments of the currently logged-in user
@profile_bp.route('/user_comments/<username>')
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
        comment.post.img_url = url_for('post.serve_uploaded_image', filename=os.path.basename(comment.post.img_path))

    # Calculate total views for the user's posts
    total_views = user.calculate_total_views()
    
    # Pass the username to the template
    username = user.username

    return render_template('user_comments.html', user=user, user_comments=user_comments, total_views=total_views, username=username)

# Route to display the about page of the user
@profile_bp.route('/user_about/<username>')
def user_about(username):
    """Display the about page of a specific user."""
    # Retrieve user information based on username (e.g., from the database)
    user = User.query.filter_by(username=username).first()
    if user:

        # Calculate total views for the user's posts
        total_views = user.calculate_total_views()

        # Pass the username to the template
        username = user.username

        return render_template('user_about.html', user=user, total_views=total_views, username=username)
    else:
        # Handle case where user is not found
        return render_template('user_not_found.html')
    
############################################################################################################
# Edit profile

@profile_bp.route('/edit_profile', methods=['GET', 'POST'])
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
            return redirect(url_for('profile.profile'))
        else:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))
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

############################################################################################################
# Delete a user 

@profile_bp.route('/user/delete', methods=['POST'])
def delete_user():
    """Delete a user."""
    if g.user:
        user_id = g.user.id

        # Delete comments by the user
        Comment.query.filter_by(fk_userid=user_id).delete()

        # Delete likes by the user
        Like.query.filter_by(user_id=user_id).delete()

        # Delete user posts
        Post.query.filter_by(fk_userid=user_id).delete()

        # Delete the user from the database
        db.session.delete(g.user)
        db.session.commit()
        
        # Logout the user after deletion
        do_logout()
        
        flash('Your account has been successfully deleted.', 'success')
        return redirect(url_for('index'))  # Redirect to the homepage or another appropriate page
    else:
        flash('You need to be logged in to delete your account.', 'error')
        return redirect(url_for('auth.login'))  # Redirect to the login page if user is not logged in