"""
Class to handle nurse related tools
"""

from typing import Optional
from healShared.sqlalchemy_setup.account.models import Role, User, UserToRoleAndHospital
from sqlalchemy import String, cast, func, or_




class FormsObject:

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

    def get_forms(self) -> dict:

        meta = {
            "forms": "test"
        }

        return meta

