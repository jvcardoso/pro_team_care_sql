"""
Models SQLAlchemy do Pro Team Care.

⚠️ DATABASE FIRST: Estes models apenas MAPEIAM tabelas existentes.
   As tabelas foram criadas manualmente no SQL Server (schema: [core]).
"""
from .base import BaseModel
from .company import Company
from .person import Person
from .pf_profile import PFProfile
from .pj_profile import PJProfile
from .establishment import Establishment
from .role import Role
from .user import User
from .user_role import UserRole
from .phone import Phone
from .email import Email
from .address import Address
from .permission import Permission, RolePermission, UserRole as UserRolePermission
from .session import UserSession
from .notification import Notification
from .menu import MenuItem, menu_item_permissions
from .activity import Activity
from .activity_content import ActivityContent
from .activity_entity import ActivityEntity
from .activity_image import ActivityImage
from .pendency import Pendency

__all__ = [
    'BaseModel',
    'Company',
    'Person',
    'PFProfile',
    'PJProfile',
    'Establishment',
    'Role',
    'User',
    'UserRole',
    'Phone',
    'Email',
    'Address',
    'Permission',
    'RolePermission',
    'UserRolePermission',
    'UserSession',
    'Notification',
    'MenuItem',
    'menu_item_permissions',
    'Activity',
    'ActivityContent',
    'ActivityEntity',
    'ActivityImage',
    'Pendency',
]
