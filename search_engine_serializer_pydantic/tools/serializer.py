# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from abc import abstractmethod
from typing import Type

from pydantic import BaseModel

from odoo.addons.connector_search_engine.tools.serializer import ModelSerializer


class PydanticModelSerializer(ModelSerializer):
    @abstractmethod
    def get_model_class(self) -> Type[BaseModel]:
        """Return the pydantic model class."""
        ...
