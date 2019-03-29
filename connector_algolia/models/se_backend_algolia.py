# Copyright 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class SeBackendAlgolia(models.Model):
    _name = "se.backend.algolia"
    _inherit = "se.backend.spec.abstract"
    _description = "Algolia Backend"

    # TODO: load values from server env
    algolia_app_id = fields.Char(string="APP ID")
    algolia_api_key = fields.Char(string="API KEY")

    def _get_api_credentials(self):
        return {"password": self.algolia_api_key}  # pragma: no cover
