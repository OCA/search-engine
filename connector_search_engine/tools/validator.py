# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import ValidationError


class SearchEngineDefaultValidator:
    def validate(self, data):
        if not data.get("id"):
            raise ValidationError(_("The key 'id' is missing in the data"))
