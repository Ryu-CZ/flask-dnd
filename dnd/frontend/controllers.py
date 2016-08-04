'''!
@brief Server front-end controllers
@date Created on Jun 18, 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
import flask
from flask import url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import forms
import string
import markdown
from dnd import docs
from werkzeug.security import check_password_hash
import datetime as dt

__all__ = (
    'init'
)

def init(app):
    '''!
    @brief Initialize Server front-end
    @param db: MongoEngine
    '''
    #prepare Server front-end
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    
    def check_user_password_hash(nickname, pwd):
        '''!
        @brief Return user only when user is found and users password hash fits, else non is returned
        @param nickname: unique user name
        @param pwd: password to check
        '''
        u = docs.User.objects.get(nickname=nickname)
        if u is not None and check_password_hash(pwhash=u.pw_hash, password=pwd):
            return u
        return None

    @login_manager.user_loader
    def load_user(user_id):
        return docs.User.objects.get(nickname=user_id)

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
    
    @app.route('/wiki')
    def wiki():
        doc = """
Chapter
=======

Section
-------

* Item 1
* Item 2
"""
        content = flask.Markup(markdown.markdown(doc))
        return flask.render_template('wiki.html',content=content, 
                                     wiki=True, title='DnD|Wiki')
    
    @app.route('/signup', methods=['GET', 'POST'], endpoint='signup')
    def signup():
        form = forms.NewPlayer(flask.request.form)
        if form.validate_on_submit():
            u = docs.User(nickname=form.nickname.data,
                          first_name=form.first_name.data, 
                          last_name=form.last_name.data, 
                          email=form.email.data,
                          city=form.city.data, 
                          country=form.country.data,
                          created=dt.datetime.utcnow(),
                          admin=False,
                          )
            u.pw_hash = u.mask_password(form.password.data)
            u.save()
            u = docs.User.objects.get(nickname=form.nickname.data)
            if u is not None and check_password_hash(pwhash=u.pw_hash, password=form.pwd.data):
                login_user(u)
                flask.flash('Welcome %s' % u.first_name, 'success')
                following = flask.request.args.get('link', None)
                return flask.redirect(following or url_for('finances', nickname=current_user.nickname))
            flask.flash('Invalid Nickname or Password!', 'error-message')
        return flask.render_template('register.html', form=form, register=True)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = forms.Login(flask.request.form)
        if form.validate_on_submit():
            user = check_user_password_hash(nickname=form.nickname.data, 
                                            pwd=form.password.data)
            if user:
                login_user(user)
                print 'loged in', current_user.nickname
                flask.flash('Welcome %s' % user.first_name, 'success')
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
            user = check_user_password_hash(nickname=form.nickname.data, 
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
                    current_user.pw_hash = current_user.mask_password(pw)
                if current_user.save():
                    flask.flash('Profile was updated.', 'success')
                else:
                    flask.flash('Cannot save changes!', 'danger')
            else:
                flask.flash('Wrong password!', 'danger')
        return flask.render_template('player.html', form=form, edit_player=True)
    