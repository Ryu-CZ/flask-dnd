'''!
@brief frontend controllers
@date Created on Jun 18, 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
import flask
from flask import url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import models
import forms
import string

__all__ = (
    'init'
)

def init(app):
    '''!
    @brief Initialise wallet API
    @param app: Flask application
    '''
    #prepare Burns api
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    
    @login_manager.user_loader
    def load_user(user_id):
        u = app.db.get_user(user_id)
        if u is not None:
            return models.User(**u)
        return None

    @login_manager.unauthorized_handler
    def unauthorized():
        return flask.render_template("401.html"), 401

    @app.route('/')
    def index_page():
        database = '(Please sign in to see database information)'
        if current_user.is_authenticated():
            database = '{2} on {0}:{1} '.format(app.config.get('MONGODB_HOST'),
                                           app.config.get('MONGODB_PORT'),
                                           app.config.get('MONGODB_DB'))
        version = getattr(app, 'version', 'unknown-version')
        return flask.render_template('front.html',database=database, 
                                     front=True, version=version)
    
    @app.route('/signup', methods=['GET', 'POST'], endpoint='signup')
    def signup():
        form = forms.NewPlayer(flask.request.form)
        if form.validate_on_submit():
            app.db.add_player(nickname=form.nickname.data, 
                              password=form.password.data, 
                              first_name=form.first_name.data, 
                              last_name=form.last_name.data, 
                              email=form.email.data,
                              city=form.city.data, 
                              country=form.country.data)
            user = app.db.check_player_password_hash(nickname=form.nickname.data, 
                                                     pwd=form.password.data)
            if user:
                login_user(models.User(**user))
                flask.flash('Welcome %s' % user.get('first_name', 'user'), 'success')
                following = flask.request.args.get('link', None)
                return flask.redirect(following or url_for('finances', nickname=current_user.nickname))
            flask.flash('Invalid Nickname or Password!', 'error-message')
        return flask.render_template('register.html', form=form, register=True)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = forms.Login(flask.request.form)
        if form.validate_on_submit():
            user = app.db.check_user_password_hash(nickname=form.nickname.data, 
                                                   pwd=form.password.data)
            print 'user', user
            if user:
                user = app.db.get_user(nickname=form.nickname.data)
                login_user(models.User(**user))
                print 'loged in', current_user
                flask.flash('Welcome %s' % user.get('first_name', 'user'), 'success')
                following = flask.request.args.get('link', None)
                return flask.redirect(following or url_for('index_page'))
            flask.flash('Invalid Nickname or Password!', 'error-message')
        return flask.render_template('login.html', form=form, login=True)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return flask.redirect(url_for('index_page'))
    
    @app.route('/player', methods=['GET', 'POST'])
    @login_required
    def edit_player():
        form = forms.EditPlayer(flask.request.form, obj=current_user)
        if form.validate_on_submit():
            user = app.db.check_user_password_hash(
                                                nickname=form.nickname.data, 
                                                pwd=form.current_password.data)
            form.nickname.data = current_user.nickname #do not change nickname
            if user:
                form.populate_obj(current_user)
                if form.new_password.data:
                    pw = form.new_password.data
                    if len(set(string.ascii_lowercase).intersection(pw)) < 1:
                        form.new_password.errors.append(
                            'Must contain lower case chars')
                    if form.new_password.errors:
                        return flask.render_template('player.html', form=form)
                    current_user.password = pw
                _ = app.db.update_user(current_user.nickname, 
                                         {'$set':current_user.as_player()})
                flask.flash('Profile was updated.', 'success')
            else:
                flask.flash('Wrong password!', 'danger')
        return flask.render_template('player.html', form=form, edit_player=True)
    