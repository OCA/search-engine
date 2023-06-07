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
    es_server_host = fields.Char(string="ElasticSearch host")
    api_key_id = fields.Char(help="Elasticsearch Api Key ID", string="Api Key ID")
    api_key = fields.Char(help="Elasticsearch Api Key")

    def _get_adapter_class(self):
        if self.backend_type == "elasticsearch":
            return ElasticSearchAdapter
        else:
            return super().get_adapter_class()
