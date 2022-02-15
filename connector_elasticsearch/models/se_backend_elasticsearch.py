# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from elasticsearch import AuthenticationException, NotFoundError

from odoo import _, fields, models
from odoo.exceptions import UserError


class SeBackendElasticsearch(models.Model):

    _name = "se.backend.elasticsearch"
    _inherit = [
        "se.backend.spec.abstract",
        "server.env.techname.mixin",
        "server.env.mixin",
    ]
    _description = "Elasticsearch Backend"

    _search_engine_name = "elasticsearch"
    _record_id_key = "id"

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

    def action_test_connection(self):
        with self.specific_backend.work_on(self._name) as work:
            adapter = work.component(usage="se.backend.adapter")
            es = adapter._get_es_client()
            try:
                es.security.authenticate()
            except NotFoundError:
                raise UserError(_("Unable to reach host."))
            except AuthenticationException:
                raise UserError(_("Unable to authenticate. Check credentials."))
            except Exception as e:
                raise UserError(
                    _("Unable to connect to ElasticSearch:") + "\n\n" + repr(e)
                )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Connection Test Succeeded!"),
                "message": _("Everything seems properly set up!"),
                "sticky": False,
            },
        }
