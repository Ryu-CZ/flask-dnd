'''!
@brief Server front-end models
@date Created on  Jun 7, 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
import datetime as dt
from werkzeug.security import generate_password_hash

__all__ = (
    'User'
)

# Define a User model
class User(object):
    # New instance instantiation procedure
    def __init__(self, nickname=None, first_name=None, last_name=None, email=None,
                 password='', city=None, country=None, status=1, admin=True, **kw):
        self.nickname = nickname
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.city = city
        self.country = country
        self.password = password
        self.created = dt.datetime.utcnow()
        self.status = status
        self.admin = True

    def __repr__(self):
        return '<User %r %r (%r)>' % (self.first_name, self.last_name, self.nickname)

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def is_authenticated(self):
        return True
    
    def is_admin(self):
        return self.admin

    def is_active(self):
        return self.status > 0

    def is_anonymous(self):
        return False

    def mask_password(self, password=None):
        if password:
            return generate_password_hash(password)
        return generate_password_hash(self.password)

    def get_id(self):
        return unicode(self.nickname)

    def as_player(self):
        r = {'nickname': self.nickname,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'city': self.city,
            'country': self.country,
            }
        if self.password:
            r['pw_hash'] = self.mask_password()   
        return r    
                #'status': self.status}