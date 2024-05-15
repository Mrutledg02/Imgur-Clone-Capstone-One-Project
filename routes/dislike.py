from flask import Blueprint, redirect, request, url_for, flash, g
from models import db, Post, Like
from routes.helpers import add_user_to_g, do_login, do_logout, CURR_USER_KEY

dislike_bp = Blueprint('dislike', __name__)

# Route to handle disliking a post
@dislike_bp.route('/post/<int:post_id>/dislike', methods=['POST'])
def dislike_post(post_id):
    """Dislike a post."""
    post = Post.query.get_or_404(post_id)
    user_id = g.user.id if g.user else None
    
    if not user_id:
        flash('User not logged in', 'error')
        return redirect(url_for('auth.login', post_id=post_id))
    
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
        return redirect(url_for('post.show_image', post_id=post_id))
    elif request.referrer and 'index' in request.referrer:
        return redirect(url_for('index'))
    else:
        # Redirect back to the referrer URL if not show_image or index
        return redirect(request.referrer or url_for('index'))