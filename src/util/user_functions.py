from typing import Optional

from util.azure_functions import AzureHandler
from util.user import User

class UserHandler:
    def __init__(self, azure_handler: AzureHandler, table_name: str = "Users"):
        self.azure_handler = azure_handler
        self.table_name = table_name

    def create_and_save_user(self, username: str, email: Optional[str] = None, password_hash="", engagement: Optional[str] = "", is_admin: Optional[bool] = False) -> None:
        """
        Save a new user to Azure Table Storage.
        This function should only be used for new users.
        The username is used as the RowKey and can be different from email.
        """
        partition_key = "UsersPartition"
        engagements: list[str] = self.azure_handler.retrieve_table_items("Engagements")

        # Create a new user with an empty password_hash
        new_user = User(username=username.lower(), email=email.lower(), partition_key=partition_key, 
                        password_hash=password_hash, engagement=engagement, is_admin=is_admin,
                        password_creation_date="2000-01-01", previous_password_hashes="")
        self.azure_handler.insert_entity(table_name=self.table_name, entity=new_user.to_entity())

        print(f"New user {username} has been successfully saved.")

        if engagement not in engagements:
            entity = {'PartitionKey': "EngagementPartition",
                  'RowKey': engagement
                  }
            self.azure_handler.insert_entity("Engagements", entity)
    
    def save_user(self, new_user: User) -> None:
        """
        Save a new user to Azure Table Storage.
        This function should only be used for new users.
        The username is used as the RowKey and can be different from email.
        """
        self.azure_handler.insert_entity(self.table_name, new_user.to_entity())

        print(f"New user {new_user.username} has been successfully saved.")


    def update_user(self, username: str) -> None:
        """
        Update an existing user's details (such as last login time).
        """

        # Retrieve the existing user
        existing_user = self.get_user(username)
        if not existing_user:
            raise ValueError(f"User with username {username} does not exist. Use save_user to create a new user.")

        # Manually created users
        if existing_user.first_time_of_use == "":
            existing_user.first_time_of_use = existing_user._get_current_time()

        # Update the last_time_of_use and login_count
        existing_user.update_last_time_of_use()
        self.azure_handler.update_entity(self.table_name, existing_user.to_entity())

        print(f"User {username} has been successfully updated.")

    def delete_user(self, username: str):
        partition_key = "UsersPartition"

        # Retrieve the existing user
        existing_user = self.get_user(username)
        if not existing_user:
            raise ValueError(f"User with username {username} does not exist. Use save_user to create a new user.")
        
        print(f"Deleting user {username}")
        self.azure_handler.delete_entity(partition_key, self.table_name, username)
    
    def update_password(self, username: str, password_hash: str):

        # Retrieve the existing user
        existing_user = self.get_user(username)
        if not existing_user:
            raise ValueError(f"User with username {username} does not exist. Use save_user to create a new user.")
        
        existing_user.update_password(password_hash)
        self.azure_handler.update_entity(self.table_name, existing_user.to_entity())
        return

    def get_user(self, username: str) -> Optional[User]:
        """
        Retrieve user details from Azure Table Storage by email and return a User object.
        """
        partition_key = "UsersPartition"
        row_key = username
        user_entity = self.azure_handler.retrieve_entity(self.table_name, partition_key, row_key)
        
        # If the user entity is found, convert it to a User object
        if user_entity:
            return User.from_entity(user_entity)
        return None  # Return None if the user doesn't exist
    
    def get_engagement_users(self, engagement: Optional[str] = None):
        if engagement != None:
            engagement_filter = f"engagement eq '{engagement}'"
            return list(self.azure_handler.retrieve_table_items(self.table_name, engagement_filter))
        return list(self.azure_handler.retrieve_table_items(self.table_name))

        
        