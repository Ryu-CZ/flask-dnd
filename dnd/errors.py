# -*- coding: utf-8 -*-
'''!
@brief Set of special errors and exceptions used by server.
@date Created on Jun 20, 2016
@author trval@kajot.cz
'''
from flask_restplus import abort


class DndExc(Exception):
    '''!
    @brief General exception of Burns. 
    Exportable to dictionary with method dict().
    @see DndExc#abort()
    '''
    def __init__(self, user_msg="", internal_msg="", resp_code=404, err_code=0):
        '''!
        @brief Constructs general exception of Burns. 
            Designed to use with flask_restplus.errors.abort(**kw)
        @param user_msg: message friendly for user
        @param internal_msg: message for developer. Serves to find, debug or eliminate the problem.
        @param resp_code: html status code (standard values 404, 403, 500,..)
        @param err_code: internal error code
        '''
        Exception.__init__(self)
        self.user_msg = user_msg
        self.internal_msg = internal_msg
        self.err_code = err_code
        self.resp_code = resp_code 
        self.msg = internal_msg
    
    def to_abort(self):
        return self.dict()
    
    def abort(self):
        abort(**self.to_abort())
        return
                  
    def dict(self):
        '''!
        @brief Creates dictionary representing this object.
        @return {"error":{"message":self.user_msg, "internal_message":self.internal_msg, "code":self.err_code, "type":type(self).__name__ }}
        '''
        return {'success':0, 'code':self.resp_code, 'message':self.user_msg, 'internal_message':self.internal_msg, 'err_code':self.err_code, 'type':type(self).__name__}
    
    def __str__(self, *args, **kwargs):
        return '{}({})'.format(type(self).__name__ , {'code':self.resp_code, 'message':self.user_msg, 'internal_message':self.internal_msg, 'err_code':self.err_code})
    

class UnexpectedExc(DndExc):
    def __init__(self, e, resp_code=500, err_code=5000):
        DndExc.__init__(self, 
                          user_msg="Unexpected Burns Exception", 
                          internal_msg=str(e), 
                          resp_code=resp_code, 
                          err_code=err_code)
        

class MethodNotAllowed(DndExc):
    def __init__(self, method="", resp_code=405, err_code=4000):
        DndExc.__init__(self, 
                          user_msg="Method {} is not allowed".format(method), 
                          internal_msg="Method {} is not allowed".format(method), 
                          resp_code=resp_code, 
                          err_code=err_code)
