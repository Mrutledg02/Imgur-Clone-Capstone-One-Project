from app import db  # Import your SQLAlchemy instance
from models import User, Post, Comment, Like  # Import your models

def create_tables():
    db.drop_all()
    db.create_all()

def populate_initial_data():
    # Create initial users
    user1 = User(username='user1', email='user1@example.com', password='password1')
    user2 = User(username='user2', email='user2@example.com', password='password2')

    # Add users to session
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

if __name__ == '__main__':
    create_tables()  # Create tables
    populate_initial_data()