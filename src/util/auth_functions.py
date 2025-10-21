import datetime
import bcrypt

# VisaCheck imports
from util.azure_functions import AzureHandler
from util.user import User

def check_password(password, user):
    return bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))

def check_password_complexity(user: User, password: str) -> tuple:
        if check_password(password, user):
            return (False, "Password cannot be the same as current password.")
        
        for prev_pw in user.previous_password_hashes:
            if prev_pw == "":
                continue
            if bcrypt.checkpw(password.encode('utf-8'), prev_pw.encode('utf-8')):
                return (False, "Password cannot be the same as a previous password.")

        if len(password) < 12:
            return (False, "Password should contain 12 or more characters.")

        criteria_met = 0

        # Check for number in password
        if any(char.isdigit() for char in password):
            criteria_met += 1
        
        if any(char.isupper() for char in password):
            criteria_met += 1

        if any(char.islower() for char in password):
            criteria_met += 1

        if any(char in " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~" for char in password):
            criteria_met += 1

        if criteria_met < 3:
            return (False, "Password should contain at least 3 of the 4 following: \n - lowercase character \n - uppercase character \n - number \n - special character")
        
        return (True, "")

def hash_password(password):
        """Hashes the password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

class AuthHandler():
    def __init__(self, azure_handler: AzureHandler):
        self.azure_handler = azure_handler

    def check_password_expiration(self, user: User) -> bool:           
        current_date = datetime.datetime.today()
        expiration_date = datetime.datetime.strptime(user.password_creation_date, "%Y-%m-%d") + datetime.timedelta(days=90)
        
        return expiration_date <= current_date