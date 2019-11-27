# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBackendElasticsearch(models.Model):

    _name = "se.backend.elasticsearch"
    _inherit = "se.backend.spec.abstract"
    _description = "Elasticsearch Backend"

    _search_engine_name = "elasticsearch"

    es_server_host = fields.Char(string="ElasticSearch host")

    @property
    def _server_env_fields(self):
        env_fields = super()._server_env_fields
        env_fields.update({"es_server_host": {}})
        return env_fields
