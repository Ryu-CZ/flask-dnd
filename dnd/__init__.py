'''!
@brief Package holds DnD server
@date Created on 18 Jun 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
import os
import atexit
from flask import Flask, send_from_directory, url_for, render_template
from flask_restful import Api
from flask_mongoengine import MongoEngine, mongoengine
from flask_pagedown import PageDown
from flask_debugtoolbar import DebugToolbarExtension
from flask_gravatar import Gravatar
from werkzeug.contrib.fixers import ProxyFix

app_version = 'v16.30.00'
__version__ = app_version


class DnD(Flask):
    '''!
    @brief Holds DnD application class
    @see Flask
    '''
    def __init__(self, *args, **kwargs):
        '''!
    	@brief Server app constructor. Includes Api constructor call.
    	'''
        Flask.__init__(self, *args, **kwargs)
        self.version = __version__
        #setup config
        import config
        self.config.from_object(config)
        self.config.from_pyfile('/etc/dnd/config.py', silent=True)
        #add favicon     
        @self.route('/favicon')   
        @self.route('/favicon.ico')
        @self.route('/static/favicon')
        @self.route('/static/favicon.ico')
        def favicon():
            return send_from_directory(os.path.join(app.root_path, 'static/images'),
                                       'favicon.ico', 
                                       mimetype='image/vnd.microsoft.icon')
        @self.errorhandler(404)
        def not_found(error):
            return render_template('404.html', error=error), 404
        
        self.before_first_request(self.ensure_connection)
        
    def ensure_connection(self):
        mongoengine.connect(app.config['MONGODB_DB'], alias=mongoengine.connection.DEFAULT_CONNECTION_NAME, host=app.config['MONGODB_HOST'])
        

app = DnD(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

db = MongoEngine(app)
pagedown = PageDown(app)

toolbar = None
if app.config.get('DEBUG_TOOLBAR_ACTIVATE', False):
    app.debug = True
    app.config['DEBUG_TB_PANELS'] = ['flask_mongoengine.panels.MongoDebugPanel']
    toolbar = DebugToolbarExtension(app)
    

gravatar = Gravatar(app,
                    size=156,
                    rating='x',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

#setup frontend
import frontend
frontend.init(app)