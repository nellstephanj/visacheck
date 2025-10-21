from datetime import datetime, timezone
import re
from typing import Optional, Dict

__PREV_PW_LIMIT__ = 10

def validate_email_format(email):
    """Simple email validation."""
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)

class User:
    def __init__(self, username: str, 
                 email: Optional[str] = None,
                 partition_key: str = "Users", 
                 first_time_of_use: Optional[str] = None, 
                 last_time_of_use: Optional[str] = None,
                 login_count: Optional[int] = 1,
                 password_hash: Optional[str] = None,
                 password_creation_date: Optional[str] = None,
                 previous_password_hashes: Optional[str] = "",
                 is_admin: Optional[bool] = False,
                 engagement: Optional[str] = ""):
        self.username: str = username # Username is required and will be the RowKey
        self.email: Optional[str] = email
        self.username: str = username if username else email
        self.partition_key: str = partition_key
        self.first_time_of_use: str = first_time_of_use if first_time_of_use is not None else self._get_current_time()
        self.last_time_of_use: str = last_time_of_use if last_time_of_use is not None else self._get_current_time()
        self.login_count: int = login_count
        self.password_hash: Optional[str] = password_hash  # Store password hash
        self.password_creation_date: Optional[str] = password_creation_date
        self.previous_password_hashes: Optional[list[str]] = previous_password_hashes.split(',')
        self.isAdmin: bool = is_admin
        self.engagement: str = engagement

        # Validate the email format if email is provided
        if email:
            self._validate_email()

    def _get_current_time(self) -> str:
        """Gets the current UTC time in ISO format with timezone information."""
        return datetime.now(timezone.utc).isoformat()

    def _validate_email(self) -> None:
        """Validates the email format."""
        if not isinstance(self.email, str) or "@" not in self.email:
            raise ValueError("Invalid email format")

    def to_entity(self) -> Dict[str, str]:
        """Converts the user object into a dictionary (entity) for Azure Table Storage."""
        return {
            'PartitionKey': self.partition_key,
            'RowKey': self.username,
            'username': self.username,
            'email': self.email,
            'first_time_of_use': self.first_time_of_use,
            'last_time_of_use': self.last_time_of_use,
            'login_count': str(self.login_count),
            'password_hash': self.password_hash or "",  # Store password hash
            'password_creation_date': self.password_creation_date,
            'previous_password_hashes': ','.join(self.previous_password_hashes),
            'is_admin': self.isAdmin,
            'engagement': self.engagement
        }

    def update_last_time_of_use(self) -> None:
        """Updates the last_time_of_use to the current time."""
        self.last_time_of_use = self._get_current_time()
        self.login_count += 1  # Increment login count on login

    def update_password(self, password_hash):
        self.password_creation_date = datetime.strftime(datetime.today(), "%Y-%m-%d")

        self.previous_password_hashes.append(self.password_hash)

        if len(self.previous_password_hashes) > __PREV_PW_LIMIT__:
            del self.previous_password_hashes[0]

        self.password_hash = password_hash

    @classmethod
    def from_entity(cls, entity: Dict[str, str]) -> "User":
        """Creates a User object from an Azure Table entity."""
        return cls(
            username=entity.get('RowKey'),  # Use RowKey as the username
            email=entity.get('email', None),  # Get the email if it exists
            partition_key=entity.get('PartitionKey', 'Users'),
            first_time_of_use=entity.get('first_time_of_use'),
            last_time_of_use=entity.get('last_time_of_use'),
            login_count=int(entity.get('login_count', 0)),
            password_hash=entity.get('password_hash'),  # Load the password hash
            password_creation_date=entity.get('password_creation_date'),
            previous_password_hashes=entity.get('previous_password_hashes'),
            is_admin=entity.get('is_admin'),
            engagement=entity.get('engagement')
        )
