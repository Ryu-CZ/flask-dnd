'''!
@brief Package holds DnD server
@date Created on 18 Jun 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
import os
import atexit
from flask import Flask, send_from_directory, url_for
from flask_restful import Api
from werkzeug.contrib.fixers import ProxyFix

app_version = 'v16.24.00'
__version__ = app_version


class Dnd(Flask):
    '''!
    @brief Holds Dnd application class
    @see Flask
    '''
    def __init__(self, *args, **kwargs):
        '''!
    	@brief Burns constructor API. Includes Api constructor call.
    	'''
        Flask.__init__(self, *args, **kwargs)
        self.version = __version__
        #setup config
        import config
        self.config.from_object(config)
        self.config.from_pyfile('/etc/burns/config.py', silent=True)
        #setup db
        from db import MongoDB
        self.db_class = MongoDB
        self.test_db()
        self.before_first_request(f=self.init_db)
        #add favicon     
        @self.route('/favicon')   
        @self.route('/favicon.ico')
        @self.route('/static/favicon')
        @self.route('/static/favicon.ico')
        def favicon():
            return send_from_directory(os.path.join(app.root_path, 'static/images'),
                                       'favicon.ico', 
                                       mimetype='image/vnd.microsoft.icon')
        #setup frontend
        import frontend
        frontend.init(self)

    
    def init_db(self, *args, **kwargs):
        '''!
        @brief Creates database handler
        If one already exists it is closed and replaced by new one
        Also automatic database close before app exit is set up with atexit lib
        '''
        self.close_db()
        self.db = self.db_class(self)
        #manage automatic database client close before app exit
        atexit.register(self.close_db)
    
    def close_db(self, *args, **kwargs):
        '''!
        @brief Ensure closing db
        '''
        if hasattr(self, 'db') and self.db:
            self.db.close()

    def test_db(self):
        '''!
        @brief Perform authorization test for default user
        '''
        print '\n{} database: data test starting'.format(self.db_class.__name__)
        db = self.db_class(self)
        print '\t testing authorization:', db.check_user_password_hash('Ajax', 'secret')
        db.close()
        db = None
        print '{} database: data test complete\n'.format(self.db_class.__name__)


app = Dnd(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)