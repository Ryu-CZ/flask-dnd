# -*- coding: utf-8 -*- 

'''!
@brief Holds database connector implementation for MongoDB.
@date Created on Jun 18, 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
import pymongo
import os
import datetime as dt
# from bson import ObjectId
from werkzeug.security import generate_password_hash


class MongoDB(object):
    '''!
    @brief Database abstraction layer for MongoDB
    '''  
    user_default = [{ "nickname":"Ajax", "admin":True, 
                       "first_name":"Francis","last_name":"Freeman","country":"US", 
                       "pw_hash":generate_password_hash("secret"),
                       "city":"Philadelphia", "currency":"USD", 'created':dt.datetime.utcnow()}
                      ]
    
    def __init__(self, app, **kwargs):
        #create mongo connection
        self.client = pymongo.MongoClient(app.config['MONGODB_HOST'],
                                              app.config['MONGODB_PORT'])
        self.db = self.client[app.config['MONGODB_DB']]
        self.pid_worker = os.getpid()
        #init collections
        self.init_user()
        
    def init_user(self):
        col = 'user'
        ix = 'search_{}'.format(col)
        if col not in self.db.collection_names(include_system_collections=False):
            self.db.create_collection(col)
        if ix not in self.db[col].index_information():
            self.db[col].create_index([("nickname", pymongo.ASCENDING)],
                                      unique=True,
                                      name=ix)
        def_data = MongoDB.user_default
        for i in range(len(def_data)):
            if 0 == self.db[col].count({"nickname":def_data[i]['nickname']}):
                self.db[col].insert_one(def_data[i])
                
    def close(self):
        '''!
        @brief Close client
        '''
        self.db = None
        self.client.close()
        self.client = None
    
    def check_user_password_hash(self, nickname, pwd):
        '''!
        @brief Return true only when user is found and users password hash fits
        @param username: unique user name
        @param pwd: password to check
        '''
        user = self.db.user.find_one({"nickname":nickname}, {"pw_hash":1})
        if user:
            return user
        return None
    
    
    def add_user(self, nickname, password, first_name, last_name, city, country, currency='EUR', date_created=None):
        '''!
        @brief Creates new user record. Do not confuse with user!! 
        @param nickname: nick of user
        @param password: password will be stored hashed
        @param first_name: first name of user
        @param last_name: surname
        @param city: City where user lives
        @param country: Country/State where user lives
        @param currency: shortcut of currency
        @param date_created: if not given, now is used
        '''
        date_created = date_created or dt.datetime.utcnow()
        return self.db.user.insert({"nickname":nickname,
                                      "pw_hash":generate_password_hash(password),
                                      "first_name":first_name,
                                      "last_name":last_name,
                                      "city":city,
                                      "country":country,
                                      "currency":currency,
                                      "real":0,
                                      "bonus":0,
                                      "date_created":date_created})
        
    def get_user(self, nickname):
        '''!
        @brief Returns user detail by its _id
        '''
        return self.db.user.find_one({"nickname": nickname})
    
    def update_user(self, nickname, changes):
        '''!
        @brief Returns user update response
        '''
        return self.db.user.update_one({"nickname":nickname}, changes)