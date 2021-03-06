'''!
@brief Configuration file of DnD
@date Created on Jun 18, 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
import os
import logging

#detail log setting
DETAIL_LOG_PATH = "/var/log/dnd/details.log"
DETAIL_LOG_LEVEL = logging.WARN
DETAIL_LOG_LEVEL_DB = logging.WARN #path to dbg is not optional and its same as LOG_PATH, so they write to same file always

#profiling log setting
PROFILE_LOG_PATH = "/var/log/dnd/profile.log"
PROFILE_LOG_LEVEL = logging.INFO

#Mongo ORM setting
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'dnd'
MONGODB_ALIAS = 'default'
if "MONGODB_URL" in os.environ:
    MONGODB_HOST, MONGODB_PORT = os.environ.get('MONGODB_URL', 'localhost:27017').lstrip('mongodb://').rstrip('/').split(':')
    MONGODB_PORT = int(MONGODB_PORT)

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret dnd"
WTF_CSRF_SECRET_KEY = 'secret wtf dnd'

# Secret key for signing cookies
SECRET_KEY = "secret"

ADMINS = frozenset(['nemo@nowhere.com'])

DEBUG_TOOLBAR_ACTIVATE = False

IMAGES_PER_PAGE = 18
WIKIS_PER_PAGE = 18
CHARACTERS_PER_PAGE = 32
