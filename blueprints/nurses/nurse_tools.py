"""
Class to handle nurse related tools
"""

from typing import Optional

from healShared.sqlalchemy_setup.account.models import Role, User, UserToRoleAndHospital
from sqlalchemy import String, cast, func, or_

# import logging
#
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def get_paginated_nurses(
    session,
    fernet_key: str,
    page: int = None,
    page_size: int = None,
    search: Optional[str] = None,
    is_count: bool = False,
):
    """

    Notes:
        https://dev.to/appwrite/this-is-why-you-should-use-cursor-pagination-4nh5
        https://planetscale.com/blog/mysql-pagination
        https://hackernoon.com/please-dont-use-offset-and-limit-for-your-pagination-8ux3u4y

        Fire an async task to update redis cache for the next page

        The code written by gino does not scale as it does a full table scan
        https://stackoverflow.com/questions/16093475/flask-sqlalchemy-querying-a-column-with-not-equals

    Args:
        session ():
        page (int): page number
        page_size (int): number of items per page
        search (str): search string
        fernet_key (str): fernet key

    Returns:

    """

    query = (
        session.query(User)  # .with_entities(User.name, User.email, User.id, User.user_role)
        .outerjoin(UserToRoleAndHospital, User.id == UserToRoleAndHospital.user_id)
        .outerjoin(Role, UserToRoleAndHospital.role_id == Role.id)
        .filter(
            User.name.isnot(None),
            User.name.isnot(None),
            or_(
                (Role.name.in_(Role.NURSE_HOSPITAL_STAFF_ROLES))
                | ~User.id.in_(
                    session.query(UserToRoleAndHospital.user_id)
                    .join(Role)
                    .filter(Role.name.in_(Role.NURSE_HOSPITAL_STAFF_ROLES))
                )
            ),
        )
    )
    if search:
        query = query.filter(
            or_(
                cast(func.aes_decrypt(User.name, fernet_key), String).like(f"%{search}%"),
                cast(func.aes_decrypt(User.email, fernet_key), String).like(f"%{search}%"),
            )
        )
    query = query.distinct()
    if page is None or page_size is None:
        # users = query.all()
        total = query.count()
        if is_count:
            return [], total
        else:
            users = query.all()
            return users, total

    users = query.offset((page - 1) * page_size).limit(page_size).all()
    total = query.count()

    return users, total


class NursesObject:

    """
    Class to handle nurse related tools
    """

    def __init__(self, parms: dict, db_api: dict) -> None:
        """

        Args:
            parms ():
            db_api ():
        """

        self.params = parms
        self.db_api = db_api

    def get_nurses(self, page: int, page_size: int, search: str, is_count: bool = False) -> dict:
        """

        Args:

            page ():
            page_size ():
            search ():
            is_count ():

        Returns:

        """

        fernet_key = self.params.get("FERNET_KEY")

        session = self.db_api["__engine_map_reader"]["session"]
        users, total = get_paginated_nurses(session, fernet_key, page, page_size, search, is_count=is_count)

        meta = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "facilities": [h.name for h in user.hospitals],
                    "activated": True if user.nurse_invitation_code else False,
                    "archived": user.is_archived,
                    "messaging": user.allow_communication_messaging,
                }
                for user in users
            ],
        }

        return meta

    def get_nurse_by_id(self, user_id: int = None, email: str = None) -> dict:
        """ """
