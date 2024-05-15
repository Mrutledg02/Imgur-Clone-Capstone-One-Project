from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import db, Comment, Post
from routes.helpers import add_user_to_g, do_login, do_logout, CURR_USER_KEY

comment_bp = Blueprint('comment', __name__)

############################################################################################################
# Comments 

# Route to add a comment to a specific post
@comment_bp.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment_to_specific_post(post_id):
    """Add a comment to a specific post."""
    data = request.form  # Assuming form data is sent via POST request
    user_id = g.user.id if g.user else None
    text = data.get('text')
    if not user_id:
            flash('User not logged in', 'error')
            return redirect(url_for('post.show_image', post_id=post_id))  # Redirect back to the post page

    success = Comment.add_post_comment(post_id, user_id, text)
    if success:
        flash('Comment added successfully', 'success')
        return redirect(url_for('post.show_image', post_id=post_id))  # Redirect back to the post page
    else:
        flash('Failed to add comment', 'error')
        return redirect(url_for('post.show_image', post_id=post_id))  # Redirect back to the post page
    

# Route to delete a comment
@comment_bp.route('/delete/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    """Delete a comment."""
    comment = Comment.query.get_or_404(comment_id)
    if comment.user != g.user:
        flash("You are not authorized to delete this comment", "error")
        return redirect(url_for('index'))
    post_id = comment.post.id  # Capture post_id before deleting the comment
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted successfully", "success")
    return redirect(url_for('post.show_image', post_id=post_id))