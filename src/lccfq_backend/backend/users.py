"""
Filename: users.py
Author: Owen Cochell
Date: 2026-04-07
Version: 1.0
Description:
    Tools for reading and writing user information, including permissions and group membership.
License: Apache 2.0
"""

from __future__ import annotations

import json
import pathlib

from abc import abstractmethod

from ..model.user import User, Group, Permissions


class BaseSerialize():
    """
    Base class for serializing and unserializing user information.

    'Serializing' is the process of converting user information
    into a format that can be stored and read later.
    This can range from persistent files to complex databases.

    This class defines the interface for serializers,
    which are intended to be lightweight and easily extendable to different storage formats.
    
    TODO:
    As of now we do not preform 'live' serialization, meaning that changes to user information are not automatically saved.
    Any changes to the user structure must be manually saved/loaded,
    which might not work with a live system like LDAP.
    """

    @abstractmethod
    def load(self, users: UserManager):
        """Serialize user information.

        :param users: The user manager containing the users to serialize.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    def dump(self, users: UserManager):
        """Unserialize user and group information.

        :param man: The user manager to populate with unserialized data.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class JSONSerialize(BaseSerialize):
    """
    A simple JSON serializer for loading/saving user data.
    """

    def __init__(self, file_path: pathlib.Path):
        self.file_path = file_path

    def dump(self, users: UserManager):
        """Dump user information to JSON.

        :param users: The user manager containing the users to dump.
        """
        data = {
            'groups': [
                {
                    'id': group.id,
                    'name': group.name,
                    'perms': group.perms.value
                }
                for group in users.groups.values()
            ],
            'users': [
                {
                    'id': user.id,
                    'name': user.name,
                    'perms': user.perms.value,
                    'groups': [group.name for group in user.groups]
                }
                for user in users.users.values()
            ]
        }

        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load(self, users: UserManager):
        """Load user and group information from JSON.

        :param users: The user manager containing the users to load.
        """
        
        # Load the JSON data from the file

        with open(self.file_path, 'r') as f:
            data = json.load(f)

        # Load each group first

        for group_data in data.get('groups', []):
            group = Group(
                id=group_data['id'],
                name=group_data['name'],
                perms=group_data['perms']
            )
            users.groups[group.name] = group

        # Load each user and their respective groups

        for user_data in data.get('users', []):
            user_groups = [users.groups[group_name] for group_name in user_data.get('groups', [])]
            user = User(
                id=user_data['id'],
                name=user_data['name'],
                perms=user_data['perms'],
                groups=user_groups
            )
            users.users[user.name] = user


class UserManager:
    """
    Manages users and their permissions.

    TODO:
    As of now, we trust the username provided by the client.
    In the future we may want to implement authentication and authorization mechanisms to verify user identities and permissions,
    likely on the gRPC side.
    """

    def __init__(self):

        self.users: dict[str, User] = {}  # Collection of users
        self.groups: dict[str, Group] = {}  # Collection of groups

    def add_user(self, user: User):
        """Add a user to the system.

        :param user: The user to add.
        """
        self.users[user.name] = user

    def has_user(self, name: str) -> bool:
        """Check if a user exists.

        :param name: The name of the user to check.
        :return: True if the user exists, False otherwise.
        """
        return name in self.users

    def get_user(self, name: str) -> User:
        """Get a user by name.

        :param name: The name of the user to get.
        :return: The user with the given name.
        """
        return self.users[name]

    def check_permission(self, user_name: str, permission: Permissions) -> bool:
        """Check if a user has a specific permission.

        :param user_name: The name of the user to check.
        :param permission: The permission to check for.
        :return: True if the user has the permission, False otherwise.
        """
        if not self.has_user(user_name):
            return False

        user = self.get_user(user_name)

        # Check direct permissions
        if user.perms & permission:
            return True

        # Check group permissions
        for group in user.groups:
            if group.perms & permission:
                return True

        return False
