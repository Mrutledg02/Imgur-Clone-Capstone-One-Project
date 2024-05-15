from flask import Blueprint, render_template, redirect, url_for, flash
from models import User, Post, Like, Comment
from routes.helpers import add_user_to_g, do_login, do_logout, CURR_USER_KEY
import os

author_profile_bp = Blueprint('author_profile', __name__)

############################################################################################################
# Author profile

#Upon clicking the author's name for a post, the user should be redirected to the author's profile page.
@author_profile_bp.route('/author/<username>')
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
        post.img_url = url_for('post.serve_uploaded_image', filename=os.path.basename(post.img_path))

    return render_template('author_profile.html', author=author, author_posts=author_posts)

# Route to display posts of a specific author
@author_profile_bp.route('/author_posts/<username>')
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
        post.img_url = url_for('post.serve_uploaded_image', filename=os.path.basename(post.img_path))

    return render_template('author_posts.html', author=author, author_posts=author_posts)

# Route to display posts liked by a specific author
@author_profile_bp.route('/author_likes/<username>')
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
        post.img_url = url_for('post.serve_uploaded_image', filename=os.path.basename(post.img_path))

    return render_template('author_likes.html', author=author, liked_posts=liked_posts)

# Route to display comments made by a specific author
@author_profile_bp.route('/author_comments/<username>')
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
        comment.post.img_url = url_for('post.serve_uploaded_image', filename=os.path.basename(comment.post.img_path))

    return render_template('author_comments.html', author=author, author_comments=author_comments)

# Route to display the about page of a specific author
@author_profile_bp.route('/author_about/<username>')
def author_about(username):
    """Display the about page of a specific author."""
    author = User.query.filter_by(username=username).first()
    if not author:
        flash('Author not found', 'error')
        return redirect(url_for('index'))

    return render_template('author_about.html', author=author)