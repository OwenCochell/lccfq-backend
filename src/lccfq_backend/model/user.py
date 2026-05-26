"""
Filename: users.py
Author: Owen Cochell
Date: 2026-05-22
Version: 1.0
Description:
    This file describes users and their permissions to be used by the backend.

License: Apache 2.0
Contact: cochell2@illinois.edu
"""

from enum import Flag, auto

from pydantic import BaseModel, Field


class Permissions(Flag):
    """Permissions that a user can have.
    """

    # Can submit circuits to the backend
    SUBMIT_CIRCUITS = auto()

    ##
    # Test permissions
    ##

    # TODO: Determine number of available tests!

    ###
    # Control Permissions
    ###

    RESET = auto()
    RETUNE = auto()
    RESETALL = auto()
    QTOL = auto()


class Group(BaseModel):
    """Groups users can be apart of
    """

    # Unique identifier for this group
    id: int

    # Name of this group
    name: str

    # Permissions this group has, encoded in bitstring
    perms: Permissions = Field(default=Permissions(0))


class User(BaseModel):
    """A user of the system
    
    Users can have permissions which describe what each user can do.
    Users can also be apart of group, which also have permissions.
    Users will have group permissions in addition to their own.
    """

    # Unique identifier for this user
    id: int

    # Name of this user
    name: str

    # Permissions this user has
    perms: Permissions = Field(default=Permissions(0))

    # Groups this user is apart of
    groups: list[Group] = Field(default_factory=list)
