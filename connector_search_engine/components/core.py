# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseSeConnectorComponent(AbstractComponent):
    _name = "base.se.connector"
    _inherit = "base.connector"
    _record_id_key = None
