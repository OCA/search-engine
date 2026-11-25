# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..tools.adapter import OpenSearchAdapter


class SeBackend(models.Model):
    _inherit = "se.backend"

    backend_type = fields.Selection(
        selection_add=[("opensearch", "OpenSearch")],
        ondelete={"opensearch": "cascade"},
        string="Type",
        required=True,
    )
    os_server_host = fields.Char(
        string="OpenSearch host",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    os_auth_type = fields.Selection(
        selection=[("http", "HTTP"), ("api_key", "API key")], default="api_key"
    )
    os_api_key_id = fields.Char(
        help="OpenSearch Api Key ID",
        string="OpenSearch Api Key ID",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    os_api_key = fields.Char(
        help="OpenSearch Api Key",
        string="OpenSearch Api Key",
        groups="connector_search_engine.group_connector_search_engine_manager",
    )
    os_user = fields.Char(help="Leave blank if not using http authentication.")
    os_password = fields.Char(help="Leave blank if not using http authentication.")
    os_ssl = fields.Boolean(
        default=True,
        help="Verify SSL certificates. Only set to False in development environments.",
    )
    os_timeout = fields.Integer(
        string="OpenSearch timeout",
        default=10,
        help="OpenSearch request timeout",
    )
    os_max_retries = fields.Integer(
        string="OpenSearch max retries",
        default=0,
        help="Number of retries, when an error occurs. "
        "0 or negative means no retries and the exception is raised.",
    )
    os_retry_on_timeout = fields.Boolean(
        string="OpenSearch retry on timeout",
        help="If set, retry when a connection timeout occurs. "
        "Otherwise, the retries are only on other errors",
    )
    os_http_compress = fields.Boolean(
        string="Compress requests/responses (gzip)",
        default=True,
        help="Enable gzip compression of the HTTP payloads exchanged with "
        "the OpenSearch cluster. Reduces network usage, at the cost of a "
        "small CPU overhead.",
    )

    @property
    def _server_env_fields(self):
        env_fields = super()._server_env_fields
        env_fields.update(
            {
                "os_server_host": {},
                "os_auth_type": {},
                "os_user": {},
                "os_password": {},
                "os_ssl": {},
                "os_api_key_id": {},
                "os_api_key": {},
            }
        )
        return env_fields

    def _get_adapter_class(self):
        if self.backend_type == "opensearch":
            return OpenSearchAdapter
        else:
            return super()._get_adapter_class()
