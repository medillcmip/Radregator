"""Exception classes for the users app"""

class BadUsernameOrPassword(Exception):
   def __init__(self, msg='Bad username or password.'):
       self.msg = msg 

   def __str__(self):
       return repr(self.msg)

class UserAccountDisabled(Exception):
   def __init__(self, msg='User account has been disabled.'):
       self.msg = msg 

   def __str__(self):
       return repr(self.msg)
