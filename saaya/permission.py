from enum import Enum


class Permission(Enum):
    OWNER = 'OWNER'
    ADMINISTRATOR = 'ADMINISTRATOR'
    MEMBER = 'MEMBER'
    ALL = 'ALL'
