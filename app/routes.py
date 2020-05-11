from flask import render_template, redirect, url_for, request
from app import app, db

from app.forms import LoginForm, RegistrationForm, UserSettingsForm, UserOrganisationForm, JoinForm

from app.models import User, Organisation
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from email_validator import validate_email, EmailNotValidError

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        print("val")
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=RegistrationForm())

@login_required
@app.route('/usersettings', methods=['GET', 'POST'])
def usersettings():
    print('a')
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = UserSettingsForm()
    if form.validate_on_submit():
        print ('b')
        if not current_user.check_password(form.confirmation.data):
            return render_template('usersettings.html', title='Settings', form=UserSettingsForm(), message = 'Wrong password, no changes made')
        username = form.change_username.data
        email = form.change_email.data
        password=form.change_password.data
        if email:
            try:
                valid = validate_email(email)
                current_user.email=valid.email
            except EmailNotValidError:
                return render_template('usersettings.html', title='Settings', form=UserSettingsForm(), message = 'No valid imput')
        if password:
            current_user.set_password(password)
        if username:
            if len(username)>2:
                current_user.username=username
            else:
                db.session.commit()
                return render_template('usersettings.html', title='Settings', form=UserSettingsForm(), message = 'No valid imput')
        db.session.commit()
        return render_template('usersettings.html', title='Settings', form=UserSettingsForm(), message = 'Your changes are made!')
    return render_template('usersettings.html', title='Settings', form=UserSettingsForm())

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route('/organisation/<name>', methods=['GET', 'POST'])
@login_required
def organisation(name):
    organisation = Organisation.query.filter_by(name=name).first_or_404()

    join_form = JoinForm()

    all_user = User.query.all()
    for u in all_user:
        if organisation in u.organisations:
            all_user.remove(u)
    add_user_form = UserOrganisationForm(obj=all_user)
    add_user_form.user.choices = [(u.id, u.username) for u in all_user]
    add_user_form.user.choices.insert(0, (-1,"choose"))

    user_in_organisation = organisation.user
    remove_user_form = UserOrganisationForm(obj=user_in_organisation)
    remove_user_form.user.choices = [(u.id, u.username) for u in user_in_organisation]
    remove_user_form.user.choices.insert(0, (-1, "choose"))

    if join_form.join.data and join_form.validate():
        organisation.add_user(current_user)
        db.session.commit()

    if add_user_form.submit.data and add_user_form.validate() and not add_user_form.user.data == -1:
        new_user_id = add_user_form.user.data
        new_user = User.query.get(new_user_id)
        organisation.add_user(new_user)
        db.session.commit()

    if remove_user_form.submit.data and remove_user_form.validate() and not remove_user_form.user.data == -1:
        old_user_id = remove_user_form.user.data
        old_user = User.query.get(old_user_id)
        organisation.remove_user(old_user)
        db.session.commit()

    all_user = User.query.all()
    for u in all_user:
        if organisation in u.organisations:
            all_user.remove(u)

    user_in_organisation = organisation.user

    add_user_form.user.choices = [(u.id, u.username) for u in all_user]
    add_user_form.user.choices.insert(0, (-1,"choose"))
    remove_user_form.user.choices = [(u.id, u.username) for u in user_in_organisation]
    remove_user_form.user.choices.insert(0, (-1, "choose"))

    return render_template('organisation.html', organisation=organisation, add_form=add_user_form, remove_form=remove_user_form, join_form=join_form)

@app.route('/organisationslist')
def organisationslist():
    organisations = Organisation.query.all()
    return render_template('organisationslist.html', organisations=organisations)
