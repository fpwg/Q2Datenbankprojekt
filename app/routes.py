from flask import render_template, redirect, url_for, request, flash, abort
from app import app, db

from app.forms import LoginForm, RegistrationForm, UserSettingsForm, OrganisationCreationForm, LeaveOrganisationFrom, CreateCategoryForm, ChangeRankForm

from app.models import User, Organisation, Rank, InventoryObject, Lend_Objects, Category, Room, Status
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
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=RegistrationForm())


@login_required
@app.route('/create_organisation', methods=['GET', 'POST'])
def register_organisation():
    form = OrganisationCreationForm()
    if form.validate_on_submit():
        organisation = Organisation.create_organisation(name=form.name.data)
        admin_rank = Rank.make_admin_rank("admin")
        organisation.ranks.append(admin_rank)
        organisation.add_user(current_user)
        db.session.add(organisation)
        db.session.commit()
        organisation.set_rank(current_user, admin_rank)
        db.session.commit()
        return redirect(organisation.page())
    return render_template('create_organisation.html', title='Create Organisation', form=OrganisationCreationForm())


@app.route('/organisations')
def organisations():
    organisations = Organisation.query.all()
    return render_template('organisation_list.html', organisations=organisations)


@app.route('/organisations/<name>')
def organisation(name):
    organisation = Organisation.query.filter_by(name=name).first_or_404()
    objects = organisation.inventoryobjects

    return render_template('organisation.html', organisation=organisation, objects=objects, current_user=current_user)


@login_required
@app.route('/organisations/<name>/ranks')
def organisation_ranks(name):
    organisation = Organisation.query.filter_by(name=name).first_or_404()
    rank = organisation.get_rank(current_user)
    if not rank or not rank.grant_ranks or not rank.edit_organisation:
        abort(404)
    ranks = organisation.ranks
    return render_template('organisation_ranks.html', ranks=ranks, organisation=organisation)


@app.route('/organisations/<org_name>/objects/<inv_id>')
def inventoryobject(org_name, inv_id):
    organisation = Organisation.query.filter_by(name=org_name).first_or_404()
    inventoryobject = InventoryObject.query.get(inv_id)

    lending_history = Lend_Objects.query.filter_by(inventory_object_id=inventoryobject.id)

    return render_template('inventoryobject.html', inventoryobject=inventoryobject, organisation = organisation, lending_history=lending_history)


@app.route('/organisations/<org_name>/categories/<cat_name>')
def category(org_name, cat_name):
    organisation = Organisation.query.filter_by(name=org_name).first_or_404()
    category = Category.query.filter_by(name=cat_name).first_or_404()

    return render_template('category.html', category=category, organisation=organisation)


@app.route('/organisations/<org_name>/statuses/<status_name>')
def status(org_name, status_name):
    organisation = Organisation.query.filter_by(name=org_name).first_or_404()
    status = Status.query.filter_by(name=status_name).first_or_404()

    return render_template('status.html', status=status, organisation=organisation)


@app.route('/rooms')
def room_list():
    rooms = Room.query.all()

    return render_template('room_list.html', rooms=rooms, current_user=current_user)


@app.route('/rooms/<name>')
def room(name):
    room = Room.query.filter_by(name=name).first_or_404()

    return render_template('room.html', room=room)


@login_required
@app.route('/usersettings', methods=['GET', 'POST'])
def usersettings():
    print('a')
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = UserSettingsForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.confirmation.data):
            return render_template('usersettings.html', title='Settings', form=UserSettingsForm(), message = 'Wrong password, no changes made')
        username = form.change_username.data
        email = form.change_email.data
        password = form.change_password.data
        bio = form.change_bio.data
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
        if bio:
            current_user.bio=bio
        db.session.commit()
        return render_template('usersettings.html', title='Settings', form=UserSettingsForm(), message = 'Your changes are made!')
    return render_template('usersettings.html', title='Settings', form=UserSettingsForm())


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    organisations = user.organisations
    return render_template('user.html', user=user, organisations=organisations, current_user=current_user)


@app.route('/organisations/<name>/leave', methods=['GET', 'POST'])
def leave_organisation(name):
    organisation = Organisation.query.filter_by(name=name).first_or_404()
    form = LeaveOrganisationFrom()

    if form.validate_on_submit():
        if form.confirm.data:
            current_user.leave_organisation(old_organisation=organisation)
            db.session.commit()
            return redirect(url_for('organisations'))
    return render_template('leave_organisation.html', form=form, organisation=organisation)


@app.route('/organisations/<name>/remove/<username>', methods=['GET', 'POST'])
def remove_user(name, username):
    organisation = Organisation.query.filter_by(name=name).first_or_404()
    user = User.query.filter_by(username=username).first_or_404()
    form = LeaveOrganisationFrom()

    if not organisation.get_rank(current_user).add_users:
        abort(404)

    if form.validate_on_submit():
        if form.confirm.data:
            user.leave_organisation(old_organisation=organisation)
            db.session.commit()
            return redirect(url_for('organisation', name=organisation.name))
    return render_template('remove_user_organisation.html', form=form, organisation=organisation, user=user)


@app.route('/organisations/<name>/join', methods=['GET', 'POST'])
def join_organisation(name):
    organisation = Organisation.query.filter_by(name=name).first_or_404()
    form = LeaveOrganisationFrom()

    if current_user.in_organisation(organisation):
        abort(404)

    if form.validate_on_submit():
        if form.confirm.data:
            organisation.add_user(current_user)
            db.session.commit()
            return redirect(url_for('organisation', name=organisation.name))
    return render_template('join_organisation.html', form=form, organisation=organisation)


@app.route('/organisations/<name>/add/<username>', methods=['GET', 'POST'])
def add_user_organisation(name, username):
    organisation = Organisation.query.filter_by(name=name).first_or_404()
    user = User.query.filter_by(username=username).first_or_404()
    form = LeaveOrganisationFrom()

    if not organisation.get_rank(current_user).add_users:
        abort(404)

    if form.validate_on_submit():
        if form.confirm.data:
            organisation.add_user(user)
            db.session.commit()
            return redirect(url_for('organisation', name=organisation.name))
    return render_template('add_user_organisation.html', form=form, organisation=organisation, user=user)


@app.route('/organisations/<name>/categories/add', methods=['GET', 'POST'])
def add_category(name):
    organisation = Organisation.query.filter_by(name=name).first_or_404()
    form = CreateCategoryForm()

    if not current_user.in_organisation(organisation):
        abort(404)

    if form.validate_on_submit():
        category_name = form.name.data
        category_description = form.description.data
        categories = Category.query.filter_by(name=category_name)
        for cat in categories:
            if cat.organisation == organisation:
                return render_template('create_category.html', form=form, organisation=organisation)
        if len(category_name) > 64 or len(category_description) > 128:
            return render_template('create_category.html', form=form, organisation=organisation)
        organisation.add_category(category_name, category_description)
        db.session.commit()
        return redirect(url_for('category', org_name=organisation.name, cat_name=category_name))

    return render_template('create_category.html', form=form, organisation=organisation)


@app.route('/organisations/<name>/statuses/add', methods=['GET', 'POST'])
def add_status(name):
    organisation = Organisation.query.filter_by(name=name).first_or_404()
    form = CreateCategoryForm()

    if not current_user.in_organisation(organisation):
        abort(404)

    if form.validate_on_submit():
        status_name = form.name.data
        status_description = form.description.data
        statuses = Status.query.filter_by(name=status_name)
        for stat in statuses:
            if stat.organisation == organisation:
                return render_template('create_status.html', form=form, organisation=organisation)
        if len(status_name) > 64 or len(status_description) > 128:
            return render_template('create_status.html', form=form, organisation=organisation)
        organisation.add_status(status_name, status_description)
        db.session.commit()
        return redirect(url_for('status', org_name=organisation.name, status_name=status_name))

    return render_template('create_status.html', form=form, organisation=organisation)


@login_required
@app.route('/rooms/add', methods=['GET', 'POST'])
def add_room():
    form = CreateCategoryForm()

    if form.validate_on_submit():
        room_name = form.name.data
        room_description = form.description.data
        if Room.query.filter_by(name=room_name).first():
            return render_template('create_room.html', form=form)
        if len(room_name) > 64 or len(room_description) > 128:
            return render_template('create_room.html', form=form)
        db.session.add(Room(name=room_name, description=room_description))
        db.session.commit()
        return redirect(url_for('room', name=room_name))

    return render_template('create_room.html', form=form)


@app.route('/organisations/<name>/ranks/add', methods=['GET', 'POST'])
def add_rank(name):
    organisation = Organisation.query.filter_by(name=name).first_or_404()
    form = ChangeRankForm()

    if not current_user.in_organisation(organisation) or not organisation.get_rank(current_user).edit_organisation:
        abort(404)

    if form.validate_on_submit():
        rank_name = form.rank_name.data
        rank_description = form.rank_description.data
        delete_organisation = form.delete_organisation.data
        grant_ranks = form.grant_ranks.data
        add_users = form.add_users.data
        edit_organisation = form.edit_organisation.data
        lend_objects = form.lend_objects.data

        ranks = Rank.query.filter_by(name=rank_name)
        for rank in ranks:
            if rank.organisation == organisation:
                return render_template('create_rank.html', form=form, organisation=organisation)
        if len(rank_name) > 64 or len(rank_description) > 128:
            return render_template('create_rank.html', form=form, organisation=organisation)
        organisation.ranks.append(Rank(name=rank_name, delete_organisation=delete_organisation, grant_ranks=grant_ranks, add_users=add_users, edit_organisation=edit_organisation, lend_objects=lend_objects))
        db.session.commit()
        return redirect(url_for('organisation_ranks', name=organisation.name))

    return render_template('create_rank.html', form=form, organisation=organisation)
