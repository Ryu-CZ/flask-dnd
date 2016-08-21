# coding=utf-8
'''!
@brief frontend forms
@date Created on Jun 6, 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
from dnd import docs
from flask_wtf import Form, file
from wtforms import PasswordField, HiddenField, StringField, TextAreaField, BooleanField, RadioField
from wtforms.fields.html5 import EmailField, DateTimeField
# Import Form validators
from wtforms.validators import Required, Email, Optional, EqualTo, ValidationError, Regexp, Length
from flask_pagedown.fields import PageDownField
import re
from werkzeug import secure_filename
# from flask_mongoengine.wtf import model_form

__all__ = (
    'Login', 'EditPlayer', 'AddCredit', 'SetCredit', 'NewPlayer', 'EditWikiPage', 'EditMainWikiPage', 'ImageUpload'
)


class UniqueItem(object):
    def __init__(self, model, elem_name, message='Unique {elem} {value} already exists'):
        self.model = model
        self.elem_name = elem_name
        self.message = message
        
    def __call__(self, form, field):
        if self.model.objects(**{self.elem_name:field.data}).count():
            raise ValidationError(self.message.format(elem=self.elem_name, 
                                                      value=field.data))

def file_renamer(s):
    return secure_filename(s.lower())

class UniqueFile(object):
    def __init__(self, model, elem_name, name_mapper=file_renamer, message="Unique {elem} '{value}' already exists"):
        self.model = model
        self.elem_name = elem_name
        self.message = message
        self.name_mapper = name_mapper
        
    def __call__(self, form, field):
        print self.name_mapper(field.data)
        print 'test'
        if self.model.objects(**{self.elem_name:self.name_mapper(field.data)}).count():
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
    email = EmailField('Email', [Optional(), 
                                Email()])
    city = StringField('City', [Optional()])
    country = StringField('Country', [Optional()])
    current_password = PasswordField('Current password', [Required()])
    new_password = PasswordField('New password', [Optional(), 
                                                  Length(min=6)])
    new_password_check = PasswordField('New password again', 
                            [EqualTo('new_password', 
                                     'Passwords must match!')])


class NewPlayer(Form):
    nickname = StringField('Nickname', [Required(), 
                                        Length(min=4), 
                                        UniqueItem(docs.User, 'nickname')])
    player_id = HiddenField()
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    email = EmailField('Email', [Required(), 
                                Email(),
                                UniqueItem(docs.User, 'email')])
    city = StringField('City', [Optional()])
    country = StringField('Country', [Optional()])
    password = PasswordField('Password', [Required(), 
                                                  Length(min=6)])
    password_check = PasswordField('Password again', 
                            [EqualTo('password', 'Passwords must match!'),
                             Required()])
    
class EditWikiPage(Form):
    name = StringField('Page Name', [Required(), Regexp(r'^([a-zA-Z0-9-_ ])+$', 
                                                        flags=re.IGNORECASE, 
                                                        message="Use only number, characters and '_'")])
    pagedown = PageDownField('Enter your markdown')
    
class EditMainWikiPage(Form):
    name = HiddenField()
    pagedown = PageDownField('Enter your markdown')


class ImageUpload(Form):
    name = StringField('Name', [Required(), UniqueFile(docs.Image, 'name')], description='Unique name of picture for future reference to it')
    description = TextAreaField('Description', default='', description='Describe your picture')
    image = file.FileField('Image File', [file.FileRequired(), 
                                          file.FileAllowed(['jpg', 'png'], 'Images only!')])
    
class ImageEdit(Form):
    pk = HiddenField()
    name = StringField('Name', [Required()], description='Unique name of picture for future reference to it')
    description = TextAreaField('Description', description='Describe your picture')
    image = file.FileField('Image File', [file.FileAllowed(['jpg', 'png'], 'Images only!')])


class ImageDetail(Form):
    pk = HiddenField()
    name = StringField('Name', readonly=True, description='Unique name of picture for future reference to it')
    created = DateTimeField('Created', readonly=True)
    author = StringField('Author', readonly=True)
    description = TextAreaField('Description', readonly=True, description='Describe your picture')
    
class NewCharacter(Form):
    name = StringField('Name', [Required(), UniqueFile(docs.Character, 'slug')], description='Unique name of character')
    is_player = BooleanField('Is the player character?', default=False)
    gender = RadioField('Gender', default='male', choices=[('male', 'male'), ('female', 'female')])
    quick_desription = StringField('Description', [Required(), Length(max=124)], default='', description='Describe your character in few worlds')
    desription = PageDownField('Enter characters description in markdown')
    biography = PageDownField('Enter characters biography in markdown')
    image = file.FileField('Character image', [file.FileAllowed(['jpg', 'png'], 'Images only!')])
    
class EditCharacter(NewCharacter):
    pk = HiddenField()
