# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ElasticsearchConnectorComponent(Component):
    _name = "elasticsearch.se.connector"
    _inherit = "base.se.connector"
    _collection = "se.backend.elasticsearch"
    _record_id_key = "objectID"
