from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
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
    submit = SubmitField('Create')

    def validate_name(self, name):
        organisation = Organisation.query.filter_by(name=name.data).first()
        if organisation is not None:
            raise ValidationError('Name is already taken.')

class UserSettingsForm(FlaskForm):
    change_username = StringField('New Username')
    change_email = StringField('New Email')
    change_bio = StringField('Write about yourself')
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

class ChangeRankForm(FlaskForm):
    rank_name = StringField()
    rank_description = StringField()
    delete_organisation = BooleanField()
    grant_ranks = BooleanField()
    add_users = BooleanField()
    edit_organisation = BooleanField()
    lend_objects = BooleanField()

    submit = SubmitField("save")

class LeaveOrganisationFrom(FlaskForm):
    # Also used for join organisation, remove and add user to organisation
    confirm = BooleanField('Confirm')
    submit = SubmitField('Submit')

class CreateCategoryForm(FlaskForm):
    # Also used for create status and room
    name = StringField()
    description = StringField()

    submit = SubmitField('Create')

class CreateObjectForm(FlaskForm):
    name = StringField()
    description = StringField()
    categories = StringField()
    status = StringField()
    room = StringField()

    submit = SubmitField('Create')

class CSVUploadForm(FlaskForm):
    upload = FileField('CSV-File')
    submit = SubmitField('Upload')
