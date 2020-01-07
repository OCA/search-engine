# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SeBackendSpecAbstract(models.AbstractModel):
    _name = "se.backend.spec.abstract"
    _description = "Se Specialized Backend"
    _inherit = "connector.backend"

    # declare a unique name for this search engine service
    # (eg: elasticsearch, algolia, my-super-engine).
    # This can be used by other modules to understand
    # which engine they are dealing with
    _search_engine_name = ""

    # Delegation inheritance
    se_backend_id = fields.Many2one(
        comodel_name="se.backend",
        ondelete="cascade",
        index=True,
        auto_join=True,
        delegate=True,
        required=True,
    )

    @api.model
    def create(self, vals):
        vals["specific_model"] = self._name
        return super(SeBackendSpecAbstract, self).create(vals)

    def unlink(self):
        se_backend = self.mapped("se_backend_id")
        res = super(SeBackendSpecAbstract, self).unlink()
        # NOTE: this will delete indexes and bindings by cascade
        se_backend.unlink()
        return res

    def _get_api_credentials(self):
        # TODO: user self.name to retrieve creds from server env
        # TODO: username password etc
        return {}  # pragma: no cover
