# coding=utf-8
'''!
@brief frontend forms
@date Created on Aug , 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
from flask_mongoengine import Document
from mongoengine import fields, NULLIFY
from werkzeug import generate_password_hash
import datetime as dt



class User(Document):
    nickname = fields.StringField(required=True, max_length=50)
    first_name = fields.StringField(required=True, max_length=50)
    last_name = fields.StringField(required=True, max_length=50)
    email = fields.EmailField(required=True)
    city = fields.StringField(max_length=80)
    country = fields.StringField(max_length=80)
    pw_hash = fields.StringField(required=True)
    created = fields.DateTimeField(required=True)
    admin = fields.BooleanField()

    def __init__(self, status=1, admin=True, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self.status = status
        self.admin = admin 
    
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
        r = {'nickname':self.nickname,
            'first_name':self.first_name,
            'last_name':self.last_name,
            'email':self.email,
            'city':self.city,
            'country':self.country,
            'created':self.created,
            'admin':self.admin
            }
        if self.password:
            r['pw_hash'] = self.mask_password()   
        return r
    
    def __repr__(self):
        return '<User: {}>'.format(self.nickname)
    
    def __str__(self):
        return '<User: {} ({})>'.format(self.nickname, self.full_name())
    

class WikiDoc(Document):
    title = fields.StringField(required=True, max_length=62)
    name = fields.StringField(required=True, max_length=62)
    create_date = fields.DateTimeField(required=True)
    edit_date = fields.DateTimeField(required=True, default=dt.datetime.utcnow)
    author = fields.ReferenceField('User')
    text = fields.StringField(required=True, default='')

User.register_delete_rule(WikiDoc, 'author', NULLIFY)