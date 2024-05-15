from flask import Blueprint, render_template, request, url_for
from models import Post
from routes.helpers import add_user_to_g, do_login, do_logout, CURR_USER_KEY
import os

search_bp = Blueprint('search', __name__, url_prefix='/search')

############################################################################################################
# Search

@search_bp.route('/search')
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