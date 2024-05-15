from flask import Flask, Blueprint, request, flash, send_from_directory, redirect, render_template, session, url_for, g
from werkzeug.utils import secure_filename
from routes.helpers import add_user_to_g, do_login, do_logout, CURR_USER_KEY

import os

from models import db, User, Comment, Post, Like, View
from forms import PostImageForm, EditPostForm

post_bp = Blueprint('post', __name__, url_prefix='/post')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

############################################################################################################
# Post upload and Post

# Route to render HTML template for uploading an image
@post_bp.route('/postImage', methods=['GET', 'POST'])
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
                return redirect(url_for('post.show_image', post_id=post.id))
        
    return render_template('postImage.html', form=form)

# Function to increment the user's upload count
def increment_user_uploads(user_id):
    """Increment the user's upload count."""
    user = User.query.get(user_id)
    if user:
        user.uploads += 1
        db.session.commit()

# Route to serve uploaded images
@post_bp.route('/uploads/<filename>')
def serve_uploaded_image(filename):
    """Serve uploaded images."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to render HTML template for displaying a post once uploaded
@post_bp.route('/image/<int:post_id>')
def show_image(post_id):
    """Display a specific post."""
    post = Post.query.get_or_404(post_id)
    img_filename = os.path.basename(post.img_path)

    # Check if the post exists
    if not post:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))

    if img_filename:
        img_url = url_for('post.serve_uploaded_image', filename=img_filename)
        comments = Comment.get_post_comments(post_id)  # Fetch comments for the post

        # Check if user is logged in
        if CURR_USER_KEY not in session:
            flash('Please login to view post.', 'error')
            return redirect(url_for('auth.login'))
        
        user_id = g.user.id if g.user else None # Pass the user ID to the template

        # Check if the current user has already liked or disliked the post
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

        # Increment post views
        Post.increment_views(post_id, user_id)

        return render_template('image.html', post=post, img_url=img_url, comments=comments,
                               already_liked=already_liked, already_disliked=already_disliked,
                               is_author=is_author, user_id=user_id)
    else:       
        flash('Error fetching image.', 'error')
        return redirect(url_for('index'))
    

# Route to handle deleting a post, and decrementing the user's upload count
def decrement_user_uploads(user_id):
    """Decrement the user's upload count."""
    user = User.query.get(user_id)
    if user and user.uploads > 0:
        user.uploads -= 1
        db.session.commit()


# Route to edit a post
@post_bp.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    """Edit a post."""
    post = Post.query.get_or_404(post_id)
    form = EditPostForm(obj=post)

    if form.validate_on_submit():
        form.populate_obj(post)

        # Handle image upload if a new image is provided
        if form.upload_image.data:
            file_uploaded = form.upload_image.data
            filename = secure_filename(file_uploaded.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_uploaded.save(file_path)
            post.img_path = file_path

        db.session.commit()
        flash('Post updated successfully', 'success')
        return redirect(url_for('post.show_image', post_id=post.id))
        
    return render_template('edit_post.html', form=form)


# Route to delete a post
@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
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

    # Delete views associated with the post
    View.query.filter_by(post_id=post_id).delete()

    # Delete the post
    db.session.delete(post)
    db.session.commit()

    # Decrement the user's upload count
    decrement_user_uploads(g.user.id)

    flash("Post deleted successfully", "success")
    return redirect(url_for('index'))

