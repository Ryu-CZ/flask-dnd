# coding=utf-8
'''!
@brief frontend forms
@date Created on Jun 6, 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
from dnd import docs
from flask_wtf import Form
from wtforms import PasswordField, HiddenField, StringField, Label
# Import Form validators
from wtforms.validators import Required, Email, Optional, Length, EqualTo, ValidationError, Regexp
from flask_pagedown.fields import PageDownField
import re

__all__ = (
    'Login', 'EditPlayer', 'AddCredit', 'SetCredit', 'NewPlayer'
)

class UniqueElem(object):
    def __init__(self, model, elem_name, message='Unique {elem} {value} already exists'):
        self.model = model
        self.elem_name = elem_name
        self.message = message
        
    def __call__(self, form, field):
        if docs.User.objects(**{self.elem_name:field.data}).count():
            raise ValidationError(self.message.format(elem=self.elem_name, 
                                                      value=field.data))


class Login(Form):
    nickname = StringField('Nickname', [
            Required(message='Forgot your nickname?')])
    password = PasswordField('Password', [
                Required(message='Must provide a password. ;-)')])


class EditPlayer(Form):
    nickname = HiddenField()
    player_id = HiddenField()
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    email = StringField('Email', [Optional(), 
                                Email()])
    city = StringField('City', [Optional()])
    country = StringField('Country', [Optional()])
    current_password = PasswordField('Current password', [])
    new_password = PasswordField('New password', [Optional(), 
                                                  Length(min=6)])
    new_password_check = PasswordField('New password again', 
                            [EqualTo('new_password', 
                                     'Passwords must match!')])


class NewPlayer(Form):
    nickname = StringField('Nickname', [Required(), 
                                        Length(min=4), 
                                        UniqueElem('user', 'nickname')])
    player_id = HiddenField()
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    email = StringField('Email', [Required(), 
                                Email(),
                                UniqueElem('player', 'email')])
    city = StringField('City', [Optional()])
    country = StringField('Country', [Optional()])
    password = PasswordField('Password', [Required(), 
                                                  Length(min=6)])
    password_check = PasswordField('Password again', 
                            [EqualTo('password', 'Passwords must match!'),
                             Required()])
    
class EditWikiPage(Form):
    name = StringField('Page Name', [Required(), Regexp(r'^([a-zA-Z0-9-_ ])+$', flags=re.IGNORECASE, message="Use only number, characters and '_'")])
    pagedown = PageDownField('Enter your markdown')
    
class EditMainWikiPage(Form):
    name = Label('wikimain','Main Wiki Name')
    pagedown = PageDownField('Enter your markdown')