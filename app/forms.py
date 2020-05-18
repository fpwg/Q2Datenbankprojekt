from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User, Organisation


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Name already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('A user with this email is already registered.')


class OrganisationCreationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Sign In')

    def validate_name(self, name):
        organisation = Organisation.query.filter_by(name=name.data).first()
        if organisation is not None:
            raise ValidationError('Name is already taken.')

class UserSettingsForm(FlaskForm):
    change_username = StringField('New Username')
    change_email = StringField('New Email')
    change_password = PasswordField('Confirm New Password')
    change_password_confirm = PasswordField('Confirm New Password', validators=[EqualTo('change_password')])
    confirmation = PasswordField('Confirm with old password', validators=[DataRequired()])
    submit = SubmitField('save changes')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Name already used.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('A user with this email is already registered.')
