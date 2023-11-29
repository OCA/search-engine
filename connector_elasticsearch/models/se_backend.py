# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..tools.adapter import ElasticSearchAdapter


class SeBackend(models.Model):
    _inherit = "se.backend"

    backend_type = fields.Selection(
        selection_add=[("elasticsearch", "ElasticSearch")],
        ondelete={"elasticsearch": "cascade"},
        string="Type",
        required=True,
    )
    es_server_host = fields.Char(
        string="ElasticSearch host",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    auth_type = fields.Selection(
        selection=[("http", "HTTP"), ("api_key", "API key")], default="api_key"
    )
    api_key_id = fields.Char(
        help="Elasticsearch Api Key ID",
        string="Api Key ID",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    api_key = fields.Char(
        help="Elasticsearch Api Key",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    es_user = fields.Char(help="Leave blank if not using http authentication.")
    es_password = fields.Char(help="Leave blank if not using http authentication.")
    ssl = fields.Boolean(
        default=True,
        help="Verify SSL certificates. Only set to False in development environments.",
    )

    @property
    def _server_env_fields(self):
        env_fields = super()._server_env_fields
        env_fields.update(
            {
                "es_server_host": {},
                "auth_type": {},
                "es_user": {},
                "es_password": {},
                "ssl": {},
                "api_key_id": {},
                "api_key": {},
            }
        )
        return env_fields

    def _get_adapter_class(self):
        if self.backend_type == "elasticsearch":
            return ElasticSearchAdapter
        else:
            return super().get_adapter_class()
