'''!
@brief Package holds DnD server
@date Created on 18 Jun 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
import os
import atexit
from flask import Flask, send_from_directory, url_for, render_template
from flask_restful import Api
from flask_mongoengine import MongoEngine
from flask_pagedown import PageDown
from flask_debugtoolbar import DebugToolbarExtension
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
        

app = DnD(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

db = MongoEngine(app)

pagedown = PageDown(app)

toolbar = None
if app.config.get('DEBUG_TOOLBAR_ACTIVATE', False):
    app.debug = True
    toolbar = DebugToolbarExtension(app)

#setup frontend
import frontend
frontend.init(app)