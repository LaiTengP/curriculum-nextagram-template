from models.base_model import BaseModel
import peewee as pw
from werkzeug.security import generate_password_hash
import re

class User(BaseModel):
    username = pw.CharField(unique=True, null=False)
    email = pw.CharField(unique=True, null=False)
    password_hash = pw.TextField(null=False)

    def validate(self):
        #username unique
        existing_user_username = User.get_or_none(User.username == self.username)
        if existing_user_username:
            self.errors.append (f'User with username: {self.username} already exist.')
        
        #email unique
        existing_user_email = User.get_or_none(User.email == self.email)
        if existing_user_email:
            self.errors.append (f'User with email: {self.email} already exist.')

        # Password should be longer than 6 characters
        if len(self.password) <= 6:
            self.errors.append ('Please provide password more than 6 characters.')

        # Password should have both uppercase and lowercase characters
        # Password should have at least one special character (REGEX comes in handy here)
        has_lower = re.search (r"[a-z]", self.password)
        has_upper = re.search (r"[A-Z]", self.password)
        has_special = re.search (r"[ \! \# \$ \% \& \' \( \) \* \+ \, \- \. \/ \: \; \< \= \> \? \@ \[ \\ \] \^ \_ \` \{ \| \} \~ ]", self.password)
        
        if has_lower and has_upper and has_special:
            self.password_hash = generate_password_hash(self.password)
        else:
            self.errors.append ("Password must contain uppercase, lowercase and special character.")