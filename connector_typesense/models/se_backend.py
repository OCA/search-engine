# Copyright 2024 Derico
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..tools.adapter import TypesenseAdapter


class SeBackend(models.Model):
    _inherit = "se.backend"

    backend_type = fields.Selection(
        selection_add=[("typesense", "Typesense")],
        ondelete={"typesense": "cascade"},
        string="Type",
        required=True,
    )
    ts_server_host = fields.Char(
        string="Typesense host",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    ts_server_port = fields.Char(
        string="Typesense port",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    ts_server_protocol = fields.Char(
        string="Typesense protocol",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    ts_server_timeout = fields.Integer(
        string="Typesense server timeout",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    ts_api_key = fields.Char(
        help="Typesense Api Key",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )

    def _get_adapter_class(self):
        if self.backend_type == "typesense":
            return TypesenseAdapter
        else:
            return super()._get_adapter_class()
