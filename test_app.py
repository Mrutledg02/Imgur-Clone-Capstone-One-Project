import unittest
from flask import g
from app import app, db
from models import User, Post

class TestAuthentication(unittest.TestCase):
    def setUp(self):
        """Set up testing environment."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///imgur_clone_db_test'
        self.client = app.test_client()

        # Create a temporary database
        db.create_all()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()

    def test_register_and_login(self):
        """Test user registration and login."""
        # Register a new user
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password',
            'password_confirm': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Login with the registered user
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """Test user logout."""
        # Login with a user
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)

        # Logout the user
        response = self.client.post('/users/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        """Test user deletion."""
        # Login as the test user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

        # Delete the user
        response = self.client.post('/user/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_profile(self):
        """Test profile editing."""
        # Login as the test user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

        # Edit the user's profile
        response = self.client.post('/edit_profile', data={'username': 'updated_username'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_register_with_weak_password(self):
        """Test user registration with a weak password."""
        # Attempt to register a new user with a weak password
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'weak',
            'password_confirm': 'weak'
        }, follow_redirects=True)
        self.assertIn(b'Password must be at least 6 characters long', response.data)

    def test_register_with_duplicate_email(self):
        """Test user registration with a duplicate email."""
        # Register a new user with an email that already exists
        existing_user = User(username='existing_user', email='test@example.com', password='password')
        db.session.add(existing_user)
        db.session.commit()

        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password',
            'password_confirm': 'password'
        }, follow_redirects=True)

        self.assertIn(b'Email address is already registered.', response.data)

    def test_register_login_and_edit_profile_with_duplicate_username(self):
        """Test user registration, login, and profile edit with a duplicate username."""
        # Register a new user
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password',
            'password_confirm': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Login with the registered user
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Attempt to edit the profile with a duplicate username
        response = self.client.post('/edit_profile', data={'username': 'testuser'}, follow_redirects=True)

        # Verify that the appropriate error message is displayed
        self.assertIn(b'Username is already taken.', response.data)

    def test_delete_non_existent_user(self):
            """Test behavior when attempting to delete a non-existent user."""
            # Simulate the user not being logged in by setting g.user to None
            with app.test_client() as client:
                with client.session_transaction() as session:
                    session.clear()

                # Attempt to delete a user that doesn't exist
                response = client.post('/user/delete', follow_redirects=True)

                # Verify that an error message is present indicating the user was not found
                self.assertIn(b'You need to be logged in to delete your account.', response.data)

    def test_edit_profile_non_existent_user(self):
        """Test behavior when attempting to edit the profile of a non-existent user."""
        # Attempt to edit the profile of a non-existent user
        response = self.client.post('/edit_profile', data={
            'username': 'nonexistentuser',
            'email': 'nonexistent@example.com',
            'password': 'password',
            'about': 'New about info'
        }, follow_redirects=True)

        # Check if the response contains the expected message
        self.assertIn(b'User not found', response.data)

    def test_login_with_incorrect_credentials(self):
        """Test logging in with incorrect username and password."""
        response = self.client.post('/login', data={
            'username': 'incorrect_username',
            'password': 'incorrect_password'
        }, follow_redirects=True)
        
        self.assertIn(b'Invalid username or password', response.data)
        self.assertEqual(response.status_code, 401)

    def test_login_with_correct_username_incorrect_password(self):
        """Test logging in with correct username but incorrect password."""
        # Register a test user
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password',
            'password_confirm': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Attempt to log in with correct username but incorrect password
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'incorrect_password'
        }, follow_redirects=True)

        # Check if the error message appears and status code is 401 (Unauthorized)
        self.assertIn(b'Invalid username or password', response.data)
        self.assertEqual(response.status_code, 401)
    
    def test_login_with_incorrect_username_correct_password(self):
        """Test logging in with correct password but incorrect username."""
        # Register a test user
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password',
            'password_confirm': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Attempt to log in with incorrect username but correct password
        response = self.client.post('/login', data={
            'username': 'incorrect_username',
            'password': 'password'
        }, follow_redirects=True)

        # Check if the error message appears and status code is 401 (Unauthorized)
        self.assertIn(b'Invalid username or password', response.data)
        self.assertEqual(response.status_code, 401)
    
    def test_login_with_special_characters(self):
        """Test logging in with special characters in the username or password fields."""
        # Attempt to log in with username and password containing special characters
        response = self.client.post('/login', data={
            'username': 'user_with_special_!@#$%^&*()_+characters',
            'password': 'password_with_special_!@#$%^&*()_+characters'
        }, follow_redirects=True)

        # Check if the error message appears and status code is 401 (Unauthorized)
        self.assertIn(b'Invalid username or password', response.data)
        self.assertEqual(response.status_code, 401)
    
    def test_register_with_existing_username(self):
        """Test registering with an already existing username."""
        # Create a user with the username 'existing_user'
        existing_user = User(username='existing_user', email='existing@example.com', password='password')
        db.session.add(existing_user)
        db.session.commit()

        # Attempt to register a new user with the same username
        response = self.client.post('/register', data={
            'username': 'existing_user',
            'email': 'new_user@example.com',
            'password': 'new_password',
            'password_confirm': 'new_password'
        }, follow_redirects=True)

        # Print the response data for debugging
        print(response.data)

        # Check if the error message appears and status code is 400 (Bad Request)
        self.assertIn(b'Username or email already exists', response.data)
        self.assertEqual(response.status_code, 400)

    def test_register_with_existing_email(self):
        """Test registering with an already existing email."""
        # Create a user with the email 'existing@example.com'
        existing_user = User(username='existing_user', email='existing@example.com', password='password')
        db.session.add(existing_user)
        db.session.commit()

        # Attempt to register a new user with the same email
        response = self.client.post('/register', data={
            'username': 'new_user',
            'email': 'existing@example.com',
            'password': 'new_password',
            'password_confirm': 'new_password'
        }, follow_redirects=True)

        # Check if the error message appears and status code is 400 (Bad Request)
        self.assertIn(b'Error in Email: Email address is already registered.', response.data)
    
    def test_register_with_password_mismatch(self):
        """Test registering with a password that doesn't match the password confirmation."""
        response = self.client.post('/register', data={
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'password123',
            'password_confirm': 'password456'  # Different password confirmation
        }, follow_redirects=True)

        # Check if the error message appears and status code is 400 (Bad Request)
        self.assertIn(b'Error in Confirm Password: Field must be equal to password.', response.data)

    def test_register_with_weak_password(self):
        """Test registering with a weak password (less than the minimum required characters)."""
        response = self.client.post('/register', data={
            'username': 'test_user',
            'email': 'test@example.com',
            'password': 'weak',
            'password_confirm': 'weak'
        }, follow_redirects=True)

        # Check if the error message appears and status code is 400 (Bad Request)
        self.assertIn(b'Password must be at least 6 characters long', response.data)

if __name__ == '__main__':
    unittest.main()