"""Exception classes for the users app"""

class BadUsernameOrPassword(Exception):
   def __init__(self, msg='Bad username or password.'):
       self.msg = msg 

   def __str__(self):
       return self.msg

class UserAccountDisabled(Exception):
   def __init__(self, msg='User account has been disabled.'):
       self.msg = msg 

   def __str__(self):
       return self.msg

class UserUsernameExists(Exception):
   def __init__(self, msg='The username is taken, please try another'):
       self.msg = msg 

   def __str__(self):
       return self.msg

class UserEmailExists(Exception):
   def __init__(self, msg='This email already exists, please try another'):
       self.msg = msg 

   def __str__(self):
       return self.msg

class UserNotAuthenticated(Exception):
   def __init__(self, msg='User is not authenticated.  Please login.'):
       self.msg = msg 

   def __str__(self):
       return self.msg

class UserNotReporter(Exception):
    def __init__(self, msg='User is not a reporter.')
        self.msg = msg
    
    def __str__(self):
        return self.msg

