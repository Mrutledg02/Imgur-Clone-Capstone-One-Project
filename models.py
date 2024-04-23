from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt, check_password_hash

bcrypt = Bcrypt()

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    uploads = db.Column(db.Integer, default=0)
    about = db.Column(db.Text) 
    total_views = db.Column(db.Integer, default=0)

    posts = db.relationship("Post", back_populates="user")
    comments = db.relationship("Comment", back_populates="user")
    likes = db.relationship("Like", back_populates="user")

    @classmethod
    def create(cls, username, email, password, password_confirm):
        # Check if password matches the confirmation
        if password != password_confirm:
            raise ValueError("Passwords do not match")

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, email=email, password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return None

    @classmethod
    def get_profile(cls, username):
        return User.query.filter_by(username=username).first()

    @classmethod
    def username_exists(cls, username):
        return User.query.filter_by(username=username).first() is None

    @classmethod
    def email_exists(cls, email):
        return User.query.filter_by(email=email).first() is None
    
    @classmethod
    def increment_total_views(cls, user_id):
        try:
            user = cls.query.get(user_id)
            user.total_views += 1
            db.session.commit()
        except Exception as e:
            print(f"Error incrementing total views for user {user_id}: {e}")

    def calculate_total_views(self):
        total_views = sum(post.views for post in self.posts)
        return total_views
    
    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}'>"

class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    img_path = db.Column(db.String(255)) 
    thumbnail = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    dislikes_count = db.Column(db.Integer, default=0)
    fk_userid = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship("User", back_populates="posts")
    comments = db.relationship("Comment", back_populates="post")
    likes = db.relationship('Like', back_populates="post")

    @staticmethod
    def find_one(post_id):
        try:
            return Post.query.filter_by(id=post_id).first()
        except Exception as e:
            print(f"Error finding post by ID: {e}")
            return None

    @staticmethod
    def find_many(keyword):
        try:
            return Post.query.filter(Post.title.ilike(f'%{keyword}%') | Post.description.ilike(f'%{keyword}%')).order_by(Post.created.desc()).all()
        except Exception as e:
            print(f"Error finding posts by keyword: {e}")
            return []

    @staticmethod
    def find_user_posts(username):
        try:
            return Post.query.join(User).filter(User.username == username).order_by(Post.created.desc()).all()
        except Exception as e:
            print(f"Error finding user posts: {e}")
            return []

    @staticmethod
    def get_most_recent(x):
        try:
            return Post.query.order_by(Post.created.desc()).limit(x).all()
        except Exception as e:
            print(f"Error getting most recent posts: {e}")
            return []

    @staticmethod
    def increment_views(post_id):
        try:
            post = Post.query.get(post_id)
            if post:
                post.views += 1
                db.session.commit()
            else:
                print(f"Post with ID {post_id} not found.")
        except Exception as e:
            print(f"Error incrementing views for post {post_id}: {e}")

    def __repr__(self):
        return f"<Post {self.id}: {self.title}>"

class Comment(db.Model):

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    fk_postid = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    fk_userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="comments")
    post = db.relationship("Post", back_populates="comments")

    @classmethod
    def get_post_comments(cls, post_id):
        return Comment.query.filter_by(fk_postid=post_id).order_by(Comment.created.desc()).all()

    @classmethod
    def add_post_comment(cls, post_id, user_id, text):
        comment = Comment(fk_postid=post_id, fk_userid=user_id, text=text)
        db.session.add(comment)
        db.session.commit()
        return True
    
class Like(db.Model):

    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_like = db.Column(db.Boolean, nullable=False)

    user = db.relationship("User", back_populates="likes")
    post = db.relationship("Post", back_populates="likes")
    