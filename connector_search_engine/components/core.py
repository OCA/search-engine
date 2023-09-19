# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseSeConnectorComponent(AbstractComponent):
    _name = "base.se.connector"
    _inherit = "base.connector"

    @property
    def _record_id_key(self):
        return self.collection._record_id_key

    def _validate_record(self, record):
        self.collection._validate_record(record)
