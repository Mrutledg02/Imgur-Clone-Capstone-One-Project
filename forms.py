from flask_wtf import FlaskForm
from models import User
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length, ValidationError

class UniqueEmail(Email):
    def __init__(self, message=None):

        if not message:
            message = 'Email address is already registered.'
        super(UniqueEmail, self).__init__(message)

    def __call__(self, form, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(self.message)
        
class UniqueUsername(object):
    def __init__(self, message=None):
        if message is None:
            message = 'Username is already taken.'
        self.message = message

    def __call__(self, form, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(self.message)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),  UniqueEmail()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long')])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class PostImageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    uploadImage = FileField('Upload Image', validators=[DataRequired()])
    submit = SubmitField('Upload')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[Optional(), Length(min=4, max=20), UniqueUsername()])
    email = StringField('Email', validators=[Optional(), Email(), UniqueEmail()])
    password = StringField('Password', validators=[Optional(), Length(min=6, message='Password must be at least 6 characters long')])
    about = TextAreaField('About', validators=[Optional(), Length(max=5000)])
    submit = SubmitField('Edit Profile')

class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    upload_image = FileField('Upload Image', validators=[Optional()])
    submit = SubmitField('Edit Post')