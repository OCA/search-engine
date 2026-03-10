# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from abc import ABC, abstractmethod

from odoo.exceptions import ValidationError
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)


class JsonValidator(ABC):
    """Base validator for the search engine."""

    @abstractmethod
    def validate(self, data) -> None:
        """Validate the data before sending it to the search engine.

        It should raise an ValidationError if the data is not valid.
        """
        ...


class DefaultJsonValidator(JsonValidator):
    """Default validator for the search engine.

    It will check that the key 'id' is present in the data.
    """

    def validate(self, data) -> None:
        if not data.get("id"):
            raise ValidationError(_lt("The key 'id' is missing in the data"))
