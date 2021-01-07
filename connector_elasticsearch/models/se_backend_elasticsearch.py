# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBackendElasticsearch(models.Model):

    _name = "se.backend.elasticsearch"
    _inherit = [
        "se.backend.spec.abstract",
        "server.env.techname.mixin",
        "server.env.mixin",
    ]
    _description = "Elasticsearch Backend"

    _search_engine_name = "elasticsearch"
    _record_id_key = "objectID"

    es_server_host = fields.Char(string="ElasticSearch host")
    # `tech_name` should come from `server.env.techname.mixin`
    # but `se.backend.spec.abstract` adds delegation inheritance
    # with `se.backend` which inherits as well from `server.env.techname.mixin`
    # hence the field is not created in this specific model table
    tech_name = fields.Char(
        related="se_backend_id.tech_name", store=True, readonly=False
    )
    api_key_id = fields.Char(help="Elasticsearch Api Key ID", string="Api Key ID")
    api_key = fields.Char(help="Elasticsearch Api Key")

    @property
    def _server_env_fields(self):
        env_fields = super()._server_env_fields
        env_fields.update({"es_server_host": {}})
        return env_fields
