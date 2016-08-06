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

_def_doc = """
Main Page
=================

Author of sites did not fill this page yet.

Possibilities of wiki
-------
* Edit [Main page]({})
* Create [new page]({})
* Format with Markdown language
* Link pages between themselves
"""


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
        u = docs.User.objects(nickname=nickname)
        print u
        if u is not None and len(u) and check_password_hash(pwhash=u[0].pw_hash, password=pwd):
                return u[0]
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
            if u is not None and check_password_hash(pwhash=u.pw_hash, password=form.password.data):
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
            form.password.data = None
        return flask.render_template('login.html', form=form, login=True)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return flask.redirect(url_for('index_page'))
    
    @app.route('/players/<nickname>', methods=['GET', 'POST'])
    @login_required
    def edit_player(nickname=None):
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

    @app.route('/wikis')
    @app.route('/wikis/<page_name>', endpoint='wiki')
    def wiki(page_name='main'):
        doc = []
        page_name = page_name.lower().replace(' ', '-')
        if current_user.is_authenticated():
            doc = docs.WikiDoc.objects(name=page_name)
        elif page_name != 'main':
            doc = [docs.WikiDoc.objects.get_or_404(name=page_name)]
        if not len(doc):
            if page_name=='main':
                doc = _def_doc.format(url_for('wiki_edit', page_name=page_name), 
                                      url_for('wiki_new', page_name='new_wiki_page'))
            else:
                return flask.redirect(url_for('wiki_new', page_name=page_name))
        else:
            doc = doc[0].text
        content = flask.Markup(markdown.markdown(doc))
        return flask.render_template('wiki.html', content=content, 
                                     wiki=True, title='DnD|Wiki')
        
            
    

    @app.route('/wikis/<page_name>/new', methods=['GET', 'POST'], endpoint='wiki_new')
    @login_required
    def wiki_new(page_name):
        page_name = page_name.lower().replace(' ', '-')
        form = forms.EditWikiPage(flask.request.form)
        if form.validate_on_submit():
            #creating new doc
            if docs.WikiDoc.objects(name=form.name.data.lower().replace(' ', '-')).count():
                flask.flash('Document with this name already exists!', 'danger')
            else:
                now = dt.datetime.utcnow()
                doc = docs.WikiDoc(title=form.name.data,
                                   name=form.name.data.lower().replace(' ', '-'),
                                   text=form.pagedown.data,
                                   author=current_user.pk,
                                   create_date=now,
                                   edit_date=now)
                doc.save()
                flask.flash('Page "{}" is saved as new.'.format(doc.title), 'success')
                #view new page after creation
                return flask.redirect(url_for('wiki', page_name=form.name.data.lower().replace(' ', '-')))
        else:
            #display page
            if docs.WikiDoc.objects(name=page_name).count():
                #page alreadz exist, redirect to edit mode
                return flask.redirect(url_for('wiki_edit', page_name=page_name))
            else:
                #pre-fill page name
                form.name.data = page_name
        return flask.render_template('wiki_new.html', form=form, 
                                     wiki=True, title='DnD|Wiki')
    
    @app.route('/wikis/<page_name>/edit', methods=['GET', 'POST'], endpoint='wiki_edit')
    @login_required
    def wiki_edit(page_name):
        form = None
        page_name = page_name.lower().replace(' ', '-')
        #Editing existing page doc
        if page_name=='main':
            form = forms.EditMainWikiPage(flask.request.form)
        else:
            form = forms.EditWikiPage(flask.request.form)
        if form.validate_on_submit():
            #write form
            text = form.pagedown.data
            doc = docs.WikiDoc.objects(name=form.name.data.lower().replace(' ', '-'))
            now = dt.datetime.utcnow()
            if 0==len(doc):
                doc = docs.WikiDoc(title=form.name.data,
                                   name=form.name.data.lower().replace(' ', '-'),
                                   text=form.pagedown.data,
                                   author=current_user.pk,
                                   create_date=now,
                                   edit_date=now)
                doc.save()
                if page_name!='main':
                    flask.flash('Page "{}" is saved as new.'.format(doc.title), 'success')
                else:
                    flask.flash('Page "{}" is saved.'.format(doc.title), 
                            'success')
            else:
                doc = doc[0]
                if page_name!='main':
                    doc.title = form.name.data
                    doc.name = form.name.data.lower().replace(' ', '-')
                doc.text = form.pagedown.data
                doc.edit_date = now
                doc.save()
                flask.flash('Page "{}" is saved.'.format(doc.title), 
                            'success')
            
        else:
            #load form
            doc = docs.WikiDoc.objects(name=page_name)
            text = ''
            if 0==len(doc):
                if page_name=='main':
                    text = _def_doc.format(url_for('wiki_edit', page_name=page_name), 
                                          url_for('wiki_new', page_name='New Wiki Page'))
                else:
                    return flask.redirect(url_for('wiki_new', page_name=page_name))
            else:
                text = doc[0].text
            #Populate form with existing data
            form.pagedown.data = text
            if page_name != 'main':
                form.name.data = doc[0].title
        return flask.render_template('wiki_new.html', form=form, 
                                     wiki=True, title='DnD|Wiki')